# -*- coding: utf-8 -*-
"""B-150 Augen-Test FEUER MEIDEN (Daniel 21.10.2026 19:29: "Feldzug soll Feuer meiden und dann teste auch wirklich mit Augen,
ob es gemieden wird"). Sandkasten (Franz' Burg, nur Soldaten abgeraeumt), Plantage 19 bei (201,99) wird von zwei Sklaven
angezuendet. Dann laufen 10 eigene Streitkolben von S nach Z quer durch die Plantage:
  gerade  - ein Laufbefehl direkt nach Z (Gegenprobe)
  meiden  - Feuer ueber denselben Datenweg wie der Feldzug (Lagebild -> waechter.lies_gebaeude/lies_bodenfeuer ->
            feldzug.feuerorte -> feldzug.feuerfreier_weg), erst zum Umweg, dann nach Z
Das Auge ist der Kern (Version >= 19): jede Zeile "IM FEUER - Einheit N" fuer einen der 10 zaehlt.
VORHER FESTGELEGT: Feuer meiden belegt, wenn im Lauf "meiden" keiner der 10 IM FEUER gemeldet wird UND im Lauf "gerade"
mindestens einer - sonst misst der Aufbau nichts. Ergebnis: daten/augen_feuer_meiden.jsonl.
Aufruf: SHC_INSTANZ=5 python werkzeug/augen_feuer_meiden.py [laeufe=gerade,meiden] [takte=1500]
"""
import json
import os
import re
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import shc  # noqa: E402
import feldzug as F  # noqa: E402
from laden import befehl  # noqa: E402
from befehl import SPIEL  # noqa: E402
from waechter import lies_gebaeude, lies_bodenfeuer  # noqa: E402
from augen_feuer import gebiet, feuer, laufen  # noqa: E402

PLANTAGE, S, Z = 19, (201, 125), (201, 75)
KERNLOG = os.path.join(SPIEL, "ucp", "villagestudio", "samurai_kern.log")
AUS = os.path.join(HIER, "..", "daten", "augen_feuer_meiden.jsonl")


def lauf(art, takte):
    print("OK:", shc.sandkasten(nur_soldaten="ja"), flush=True)
    print("Gebiet S %s = %d, Z %s = %d" % (S, gebiet(*S), Z, gebiet(*Z)), flush=True)
    sk = shc.setze(spieler=1, typ=71, x=197, y=99, anzahl=2)
    s_nrs = [int(x) for x in re.search(r"Nummern \[([0-9, ]+)\]", sk).group(1).split(",")]
    laufen(3, 40)
    befehl({"angriff": {"einheiten": s_nrs, "gebaeude": PLANTAGE}}, 1.0)
    t0 = shc.zustand()["tick"]
    while feuer(PLANTAGE) < 100 and shc.zustand()["tick"] < t0 + 900:
        laufen(50)
    if feuer(PLANTAGE) < 100:
        raise SystemExit("FEHLER: Plantage brennt nach 900 Takten nicht (Feuer %d)" % feuer(PLANTAGE))
    kolben = shc.setze(spieler=1, typ=26, x=S[0], y=S[1], anzahl=10)
    k_nrs = [int(x) for x in re.search(r"Nummern \[([0-9, ]+)\]", kolben).group(1).split(",")]
    log_ab = sum(1 for _ in open(KERNLOG, encoding="utf-8", errors="replace"))
    laufen(3, 40)
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    orte = F.feuerorte(lies_gebaeude(), lies_bodenfeuer())
    weg = [Z] if art == "gerade" else F.feuerfreier_weg(S, Z, orte)
    print("%s: %d Feuer (z. B. %s), Weg %s" % (art, len(orte), orte[:3], weg), flush=True)
    t_start = shc.zustand()["tick"]
    from waechter import lies_lagebild
    befehl({"angriff": {"einheiten": k_nrs, "lauf": [weg[0][0], weg[0][1]]}}, 1.0)
    wege = [weg]
    # wie der Lenker je Runde (19:38: einmal berechnet reichte nicht, das Feuer waechst): alle 100 Takte von der Mitte der
    # Gruppe neu rechnen - bei "meiden" mit den Feuern dieser Runde, bei "gerade" bleibt es Z
    while shc.zustand()["tick"] < t_start + takte:
        laufen(100)
        if art == "gerade":
            continue
        befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
        L = lies_lagebild(neu_holen=False)
        da = [L[n] for n in k_nrs if n in L]
        if not da:
            break
        m = (sorted(e["x"] for e in da)[len(da) // 2], sorted(e["y"] for e in da)[len(da) // 2])
        orte = F.feuerorte(lies_gebaeude(), lies_bodenfeuer())
        w = F.feuerfreier_weg(m, Z, orte)
        if w != wege[-1]:
            wege.append(w)
            befehl({"angriff": {"einheiten": k_nrs, "lauf": [w[0][0], w[0][1]]}}, 1.0)
    weg = wege
    zeilen = open(KERNLOG, encoding="utf-8", errors="replace").read().splitlines()[log_ab:]
    im_feuer = sorted({int(m.group(1)) for z in zeilen for m in [re.search(r"IM FEUER - Einheit (\d+)", z)] if m
                       and int(m.group(1)) in k_nrs})
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    from waechter import lies_lagebild
    L = lies_lagebild(neu_holen=False)
    ende = sorted((n, L[n]["x"], L[n]["y"], L[n]["leben"]) for n in k_nrs if n in L)
    return {"art": art, "weg": weg, "feuer": len(orte), "im_feuer": im_feuer, "einheiten": k_nrs, "ende": ende,
            "kernzeilen": [z for z in zeilen if "IM FEUER" in z][:20]}


def main(laeufe=("gerade", "meiden"), takte=1500):
    erg = {art: lauf(art, takte) for art in laeufe}
    for art, r in erg.items():
        print("%s: IM FEUER %d von 10 %s, Weg %s" % (art, len(r["im_feuer"]), r["im_feuer"], r["weg"]), flush=True)
    urteil = None
    if "gerade" in erg and "meiden" in erg:
        if not erg["gerade"]["im_feuer"]:
            urteil = "UNGUELTIG: auch geradeaus meldete das Auge niemanden im Feuer - der Aufbau misst nichts"
        elif not erg["meiden"]["im_feuer"]:
            urteil = "BELEGT: meiden 0 im Feuer, geradeaus %d" % len(erg["gerade"]["im_feuer"])
        else:
            urteil = "WIDERLEGT: auch mit Umweg %d im Feuer" % len(erg["meiden"]["im_feuer"])
    print("ERGEBNIS:", urteil, flush=True)
    with open(AUS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "laeufe": erg, "urteil": urteil}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    main(tuple(a.get("laeufe", "gerade,meiden").split(",")), int(a.get("takte", 1500)))
