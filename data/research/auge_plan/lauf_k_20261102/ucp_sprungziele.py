# -*- coding: utf-8 -*-
"""B-142 Lauf K: Was tun die UCP-Stuecke, auf die selectAttackTarget, assignAttackTargetsForTribe und setCurrentAttackStrength springen? Liest den Code aus dem Speicher der Laufinstanz und zerlegt ihn. Liest nur.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/ucp_sprungziele.py 2 > data/research/auge_plan/lauf_k_20261102/ucp_sprungziele.txt
"""
import struct
import sys

import capstone

from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

q = ProzessQuelle(pid_der_instanz(int(sys.argv[1])))
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
STELLEN = {"selectAttackTarget": 0x4d477b, "assignAttackTargetsForTribe": 0x524633, "setCurrentAttackStrength": 0x4cde60, "updateAIStrengthState 0x4d34a8": 0x4d34a8, "aiCreateSiegeUnits 0x4d2090": 0x4d2090, "recomputeAttackInfo 0x51ef10": 0x51ef10}


def zeige(adr, n=64, tiefe=0):
    roh = q.lies(adr, n * 8)
    sprung = []
    for i, ins in enumerate(md.disasm(roh, adr)):
        if i >= n:
            break
        print(f"  {ins.address:08x} {ins.mnemonic} {ins.op_str}")
        if ins.mnemonic in ("jmp", "call") and ins.op_str.startswith("0x"):
            z = int(ins.op_str, 16)
            if z >= 0x1000000 or z < 0x400000:
                sprung.append(z)
        if ins.mnemonic == "ret":
            break
        if ins.mnemonic == "jmp" and tiefe > 0 and i > 2:
            break
    return sprung


for name, adr in STELLEN.items():
    print("=====", name, hex(adr))
    ziele = zeige(adr, 16)
    for z in dict.fromkeys(ziele):
        print("  --- Sprungziel", hex(z))
        for y in dict.fromkeys(zeige(z, 90, 1)):
            print("    --- weiter", hex(y))
            zeige(y, 60, 1)
