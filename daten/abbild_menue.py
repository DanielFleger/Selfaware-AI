# B-159 (21.10.2026 23:58): Abbild von GameSynchronyState (0x0191D768, 0x10A000 Byte) und GameCore (0x01FE7D10, 0x4000 Byte)
# im Hauptmenue - einmal nach Ladevorgaengen, einmal nach frischem Start; der Unterschied zeigt, was ein Neustart zuruecksetzt.
# Aufruf: SHC_INSTANZ=5 python daten/abbild_menue.py <name>
import os, sys
import numpy as np
os.environ.setdefault("SHC_INSTANZ", "5")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "werkzeug"))
import speicher
BEREICHE = {"gss": (0x0191D768, 0x10A000), "core": (0x01FE7D10, 0x4000)}
aus = os.path.join(os.path.dirname(os.path.abspath(__file__)), "abbild_menue_%s.npz" % sys.argv[1])
np.savez(aus, **{k: np.frombuffer(speicher.lies(a, n), dtype=np.uint8) for k, (a, n) in BEREICHE.items()})
print("ABBILD", aus, "Ansicht", int.from_bytes(speicher.lies(0x01FE7D1C, 4), "little"))
