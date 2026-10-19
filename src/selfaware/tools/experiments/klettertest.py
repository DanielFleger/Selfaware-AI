# -*- coding: utf-8 -*-
"""Klettertest - klettern unsere Assassinen auf Befehl an Rotkaeppchens Mauer? (Plan_Lord.md "EFFEKTIVER TESTEN" 2:
eine Mechanik einzeln pruefen, bevor sie in den Lenker kommt; Daniel 05.10. 21:58 "gerne").

Hintergrund (abgelesen 05.10., research/native/dekomp_klettern.c): Der Wegfinder sucht nur dann einen Kletterweg, wenn das Merkmal
"Gruppe nur aus Assassinen" gesetzt ist. Der Menschen-Laufbefehl (Spielbefehl 17, giveTribeMoveInstruction) prueft das
und sucht gezielt mit Klettern (findPathUsingClimbingWithHeightMargin16). Unser Lenker schickt bisher nur Befehl 36
(Angreifen). Neu im Modul: {"angriff": {"einheiten": [...], "lauf": [x, y]}} = Befehl 17.

VORHER FESTGELEGT (05.10. 22:05, bevor gemessen wurde):
  KLETTERN BELEGT   : der Assassine war mindestens einmal in Zustand 126 (Haken werfen) oder 127 (hochklettern)
                      UND kam dem Ziel auf <= 1 Feld nahe.
  WIDERLEGT         : in der ganzen Messzeit nie 126/127, oder er bleibt > 2 Felder vor dem Ziel stehen.
  GEGENPROBE        : ein Speertraeger mit demselben Befehl darf NIE 126/127 zeigen. (Zeigt er sie, misst das Werkzeug
                      falsch.) Steht er am Ende trotzdem auf der Mauer, gibt es dort eine Treppe - dann beweist "auf der
                      Mauer angekommen" nichts, nur der Kletterzustand zaehlt.
  ALTER BEFEHL      : ein Assassine mit dem bisherigen Befehl 36 auf den Lord - klettert er auch (126/127) oder bleibt er
                      vor der Mauer stehen? Das beantwortet, warum sie in Serie a vor den Mauern standen.

Aufruf (Spiel pausiert, Testsperre geholt):
  SHC_INSTANZ=1 uv run python -m selfaware.tools.experiments.klettertest auftraege=263:lauf:219,284;267:lauf:221,283;265:lord;171:lauf:219,284 [ticks=1600] [schritt=20] [laden=<Spielstand>]
  auftrag = nr:lauf:x,y  oder  nr:lord (Befehl 36 auf den feindlichen Lord)
Ergebnis: data/research/klettertest_<zeit>.jsonl (je Schritt und Einheit eine Zeile) und eine Zusammenfassung mit Urteil.
"""

from selfaware import workspace as _workspace
import json, os, sys, time

import selfaware.game.ucp.befehl as kanal
from selfaware.game.ucp.befehl import sende
from selfaware.game.ucp.laden import peek
from selfaware.game.ucp.steuerkarte import laufe

D = os.path.join(_workspace.DATA)
EINHEITEN, GROESSE = 0x0138854C, 1168
KLETTERN = {126: "Haken", 127: "hoch", 128: "oben-ab", 129: "runter"}
# Felder der Einheit (struktur_Unit.txt, Offsets dezimal ab unserer Basis)
FELDER = {"lebt": (140, 2), "typ": (142, 2), "besitzer": (150, 2), "kletterhoehe": (186, 2), "gebaeudehoehe": (188, 2),
          "x": (196, 2), "y": (198, 2), "zielx": (200, 2), "ziely": (202, 2), "wegplan": (252, 2), "zustand": (704, 2),
          "gruppe": (728, 2), "kann_klettern": (864, 2), "kletterzustand": (868, 4), "darf_nicht": (880, 2),
          "zielart": (924, 2), "zieleinheit": (926, 2), "leben": (968, 4), "hoehenunterschied": (1044, 2)}


def einheit(nr):
    worte = peek(EINHEITEN + nr * GROESSE, GROESSE // 4)
    b = b"".join(w.to_bytes(4, "little") for w in worte)
    return {k: int.from_bytes(b[o:o + n], "little", signed=True) for k, (o, n) in FELDER.items()}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    kanal.belege()
    if arg.get("laden"):
        from selfaware.game.ucp.laden import lade_stand
        print("geladen, Tick", lade_stand(arg["laden"], mit_bild=False))
        sende({"befehle": [{"eigenerPlatz": 1}]}, 0.8)
    ticks, schritt = int(arg.get("ticks", 1600)), int(arg.get("schritt", 20))
    import selfaware.micro.tasks.waechter as waechter
    L = waechter.lies_lagebild(True)
    lord = next((n for n, e in L.items() if e["typ"] == 55 and e["besitzer"] not in (0, 1)), None)
    auftraege = []
    for teil in arg["auftraege"].split(";"):
        s = teil.split(":")
        a = {"nr": int(s[0]), "art": s[1]}
        if s[1] == "lauf":
            a["ziel"] = tuple(int(v) for v in s[2].split(","))
        else:
            a["ziel"] = (L[lord]["x"], L[lord]["y"])
        auftraege.append(a)
    t0 = peek(0x0117CADC)[0]
    pfad = os.path.join(D, "klettertest_%s.jsonl" % time.strftime("%Y%m%d-%H%M%S"))
    proto = open(pfad, "w", encoding="utf-8")
    proto.write(json.dumps({"start_tick": t0, "auftraege": auftraege, "lord": lord}) + "\n")
    stand = {}
    for a in auftraege:
        e = einheit(a["nr"])
        stand[a["nr"]] = {"auftrag": a, "typ": e["typ"], "start": (e["x"], e["y"]), "leben0": e["leben"], "zustaende": set(),
                          "kletter": [], "min_abst": schach((e["x"], e["y"]), a["ziel"]), "max_hoehe": e["kletterhoehe"],
                          "wegplan0": None, "steht_seit": None, "letzt": (e["x"], e["y"])}
        if a["art"] == "lauf":
            sende({"befehle": [{"angriff": {"einheiten": [a["nr"]], "lauf": list(a["ziel"])}}]}, 0.6, bis="ANGRIFF eingereiht")
        else:
            sende({"befehle": [{"angriff": {"einheiten": [a["nr"]], "ziel": lord}}]}, 0.6, bis="ANGRIFF eingereiht")
        print("Auftrag", a, "- Einheit Typ %d bei %s, Abstand %d" % (e["typ"], stand[a["nr"]]["start"], stand[a["nr"]]["min_abst"]))
    t = t0
    while t < t0 + ticks:
        t = laufe(schritt)
        fertig = 0
        for a in auftraege:
            s, e = stand[a["nr"]], einheit(a["nr"])
            pos = (e["x"], e["y"])
            abst = schach(pos, a["ziel"])
            if s["wegplan0"] is None and e["wegplan"] > 0:
                s["wegplan0"] = e["wegplan"]
            s["zustaende"].add(e["zustand"])
            s["z_jetzt"] = e["zustand"]
            if e["zustand"] in KLETTERN:
                s["kletter"].append((t, KLETTERN[e["zustand"]], pos))
            s["min_abst"] = min(s["min_abst"], abst)
            s["max_hoehe"] = max(s["max_hoehe"], e["kletterhoehe"])
            s["steht_seit"] = (s["steht_seit"] or t) if pos == s["letzt"] else None
            s["letzt"], s["ende"], s["leben"], s["lebt"] = pos, pos, e["leben"], e["lebt"] != 0 and e["besitzer"] == 1
            proto.write(json.dumps(dict(e, tick=t, nr=a["nr"], abst=abst)) + "\n")
            if not s["lebt"] or (s["steht_seit"] is not None and t - s["steht_seit"] >= 200):
                fertig += 1
        print("Tick %d: %s" % (t, "  ".join("%d %s z%d h%d a%d" % (a["nr"], stand[a["nr"]]["letzt"], stand[a["nr"]]["z_jetzt"],
              stand[a["nr"]]["max_hoehe"], schach(stand[a["nr"]]["letzt"], a["ziel"])) for a in auftraege)), flush=True)
        if fertig == len(auftraege):
            print("alle stehen seit >= 200 Ticks oder sind tot - Ende")
            break
    proto.close()
    print("\n== ERGEBNIS (Protokoll %s)" % pfad)
    for a in auftraege:
        s = stand[a["nr"]]
        kletterte = bool(s["kletter"])
        art = "Assassine" if s["typ"] == 73 else "Typ %d" % s["typ"]
        if s["typ"] == 73 and a["art"] == "lauf":
            urteil = "KLETTERN BELEGT" if kletterte and s["min_abst"] <= 1 else "WIDERLEGT"
        elif s["typ"] != 73:
            urteil = "Gegenprobe ok (kletterte nicht)" if not kletterte else "Gegenprobe ROT - Werkzeug misst falsch"
        else:
            urteil = "alter Befehl: kletterte" if kletterte else "alter Befehl: kletterte NICHT"
        print("%d %s, %s auf %s: Start %s -> Ende %s, naechster Abstand %d, Kletterzustaende %s, hoechste Kletterhoehe %d, "
              "Wegplan %s, Leben %d -> %d, lebt %s => %s" % (
                  a["nr"], art, a["art"], a["ziel"], s["start"], s.get("ende"), s["min_abst"],
                  [k[:2] for k in s["kletter"][:6]] or "keine", s["max_hoehe"], s["wegplan0"], s["leben0"], s.get("leben", -1),
                  s.get("lebt"), urteil))
    sende({"befehle": [{"pause": True}]}, 0.5)


if __name__ == "__main__":
    main()
