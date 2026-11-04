# -*- coding: utf-8 -*-
"""B-142: Wie code_abgleich.py, aber fuer die festen Tabellen des Spiels: Programmdatei auf der Platte gegen den Speicher. Liest nur, aendert nichts.

Der Code-Abgleich sieht nur Befehle. Lebenspunkte, Schadenstabellen, Preise stehen in den Daten-Abschnitten. Was dort abweicht, hat UCP3 oder das Spiel beim Laufen geschrieben: Darum zaehlt nur, was fest bleibt (zwei Lesungen im Abstand, beide gleich, beide anders als die Datei).

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/daten_abgleich.py <prozessnummer> > data/research/auge_plan/lauf_s_20261103/daten_abgleich.txt
"""
import struct
import sys
import time

from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle


def abschnitte(roh):
    pe = struct.unpack_from("<I", roh, 0x3c)[0]
    n = struct.unpack_from("<H", roh, pe + 6)[0]
    opt = struct.unpack_from("<H", roh, pe + 20)[0]
    basis = struct.unpack_from("<I", roh, pe + 52)[0]
    aus = []
    for i in range(n):
        s = pe + 24 + opt + 40 * i
        name = roh[s:s + 8].rstrip(b"\0").decode("latin1")
        vgr, vadr, rgr, radr = struct.unpack_from("<IIII", roh, s + 8)
        aus.append((name, basis + vadr, vgr, radr, rgr))
    return aus


def main(pid):
    q = ProzessQuelle(pid)
    roh = open(q.pfad, "rb").read()
    print("Programm:", q.pfad, "Groesse", len(roh))
    for name, adr, vgr, radr, rgr in abschnitte(roh):
        print(f"Abschnitt {name} Adresse {adr:#x} Speichergroesse {vgr} Dateigroesse {rgr}")
        if name not in (".rdata", ".data"):
            continue
        n = min(vgr, rgr)
        datei = roh[radr:radr + n]
        eins = q.lies(adr, n)
        time.sleep(2.0)
        zwei = q.lies(adr, n)
        worte = n // 4
        d = struct.unpack("<%dI" % worte, datei[:worte * 4])
        a = struct.unpack("<%dI" % worte, eins[:worte * 4])
        b = struct.unpack("<%dI" % worte, zwei[:worte * 4])
        fest = [i for i in range(worte) if a[i] == b[i] and a[i] != d[i]]
        beweglich = sum(1 for i in range(worte) if a[i] != b[i])
        print(f"   Worte {worte}, fest anders {len(fest)}, bewegen sich gerade {beweglich}")
        # zusammenhaengende Stuecke
        stuecke = []
        for i in fest:
            if stuecke and i - stuecke[-1][-1] <= 4:
                stuecke[-1].append(i)
            else:
                stuecke.append([i])
        print(f"   Stuecke {len(stuecke)}")
        for s in stuecke:
            von, bis = adr + s[0] * 4, adr + s[-1] * 4
            print(f"   {von:#x} bis {bis:#x} ({len(s)} Worte): Datei {[d[i] for i in s[:8]]} Speicher {[a[i] for i in s[:8]]}")


if __name__ == "__main__":
    main(int(sys.argv[1]))
