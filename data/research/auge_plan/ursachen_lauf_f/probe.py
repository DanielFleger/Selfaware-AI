# -*- coding: utf-8 -*-
"""Lauf F, Ursachen: Kalender, Bau an erlaubter Stelle, Kaserne ohne Stein, Waren ueber Startwaren. Je Schritt 600 Takte = 3 Wochen, haelt von selbst an."""
import json, struct, sys, time
sys.path.insert(0, "src")
from selfaware.game.ucp import laden, bauen
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz
from selfaware.tools.analysis.auge_feldkarte import Feldkarte

AUS = sys.argv[1]
q = ProzessQuelle(pid_der_instanz(2))
k = Feldkarte.laden()
i32 = lambda a: struct.unpack("<i", q.lies(a, 4))[0]
T, P, ANSICHT, BASIS = 0x0117CADC, 0x01FEA054, 0x01FE7D1C, 0x0115BDF8 + 0x39F4
TAB = k.adresse("DAT_GameCore", "activeMenuTab.tabType")[0] if False else None
try:
    TAB = k.adresse("DAT_GameCore", "activeMenuTab")[0]
except Exception:
    TAB = None
protokoll = []


def flagge():
    a = struct.unpack("<I", q.lies(0x00DF42B4, 4))[0]
    for _ in range(80):
        if not a:
            return None
        if i32(a + 8) == 20:
            return i32(a + 0xC)
        a = struct.unpack("<I", q.lies(a + 0x20, 4))[0]
    return None


def stand(name):
    w = struct.unpack("<25i", q.lies(BASIS + 0x4D0, 100))
    s = struct.unpack("<25i", q.lies(BASIS + 0x46C, 100))
    e = {"schritt": name, "takt": i32(T), "pause": i32(P), "anzeige20": flagge(), "jahr": i32(0x117cab8), "monat": i32(0x117cab0 + 4) if False else None,
         "woche": i32(0x117cab0), "wochentakte": None, "hatBurgKorn": i32(0x117c790), "kornspeicher_id": i32(BASIS + 0xE4), "ansicht": i32(ANSICHT),
         "reiter": i32(TAB) if TAB else None, "holz": w[2], "stein": w[4], "apfel": w[13], "gold": w[15], "start_stein": s[4], "start_apfel": s[13]}
    protokoll.append(e)
    print(json.dumps(e, ensure_ascii=False), flush=True)
    json.dump(protokoll, open(AUS, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return e


def laufe(n):
    t0 = i32(T)
    laden.befehl({"tickpause": {"bei": t0 + n}}, 0.2)
    laden.befehl({"pause": False}, 0.1)
    ende = time.time() + 30  # Schutz gegen Haengen: 600 Takte brauchen bei gemessenen 825 je Sekunde unter 1 s
    while time.time() < ende:
        if i32(T) >= t0 + n and i32(P) == 1:
            return i32(T) - t0
        time.sleep(0.02)
    laden.befehl({"pause": True}, 0.2)
    raise RuntimeError("Takte kamen nicht an: %d -> %d" % (t0, i32(T)))


vorher = stand("0 vorher")
if vorher["pause"] != 1:
    raise SystemExit("Spiel laeuft, Probe abgebrochen")
g = bauen.NACH_TYP
laden.befehl({"baue": {"mapper": g[19]["mapper"], "x": 205, "y": 181, "groesse": g[19]["b"], "richtung": 0}}, 0.2)
laufe(600)
a = stand("1 Kornspeicher befohlen")
print("Kornspeicher:", bauen.gebaeude_von(1, 19), flush=True)
laden.befehl({"baue": {"mapper": g[9]["mapper"], "x": 221, "y": 179, "groesse": g[9]["b"], "richtung": 0}}, 0.2)
laufe(600)
b = stand("2 Kaserne ohne Stein befohlen")
print("Kaserne:", bauen.gebaeude_von(1, 9), flush=True)
laden.befehl({"poke": BASIS + 0x46C + 4 * 4, "wert": 100}, 0.2)
laufe(600)
c = stand("3 Startware Stein 100")
laufe(600)
d = stand("4 danach")
if d["anzeige20"]:
    menue = int(sys.argv[2])
    laden.befehl({"menue": menue}, 0.3)
    laufe(600)
    e = stand("5 Baumenue geoeffnet")
    laufe(600)
    stand("6 danach")
