# -*- coding: utf-8 -*-
"""Abstandsreihe fuer Laufwege (Daniel 06.10. 20:15: "alle moeglichen Wege durch Gebaeude durch und dann natuerlich
Tests mit allen moeglichen Abstaenden, die 2-3-4 Gebaeude voneinander haben koennen").

Messpartie, KEIN Benchmark: Baukosten der Testgebaeude werden fuer die Dauer der Messung auf 0 gesetzt (Tabelle
0x01124CF4, int[110][5]) und am Ende zurueckgeschrieben (Rueckweg im finally, alte Werte auch in der Ergebnisdatei).

Gemessen wird die Weg-Ebene des Spiels (PathLinkageLayer, Modulbefehl "wegkarte") - also was das Spiel als Schritt
erlaubt. Ob Einheiten wirklich so laufen, prueft ein eigener Lauftest (Wissensregister: bis dahin "ungeprueft").
  1. Grundriss je Gebaeudeart: welche Felder gesperrt / begehbar / nur Einbahn.
  2. Paare: gerade nebeneinander (O-W und N-S) mit 0-3 Feldern Abstand, ueber Eck (SO und NO) mit 0/1 Feld je Richtung.
     Frage je Fall: gibt es einen Weg HINDURCH (Suche auf das Rechteck um beide begrenzt, drumherum zaehlt nicht)?
  3. Drei in einer Reihe (Abstaende 0/1) und vier im Quadrat (Abstaende 0-2): Weg durch jede Luecke.
Ergebnis: data/research/wege_abstand_<zeit>.json + Bilder data/research/wege_abstand/<fall>.png
Aufruf: uv run python -m selfaware.tools.experiments.wege_abstand [nur=grundriss|paare|gruppen] [tempo=100]
"""

from selfaware import workspace as _workspace
import json
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
from selfaware.game.ucp.laden import befehl, peek
from selfaware.tools.experiments.streitkolben_messen import setze, warte_ticks, GOLD

D = os.path.join(_workspace.DATA)
BILDER = os.path.join(D, "wege_abstand")
SP = 1
KOSTEN = 0x01124CF4
# Name: (Typ = Index der Kostentabelle, Bau-Nummer (mapper), Groesse)   aus VillageStudio lib/gebaeude.json
ART = {"Schmiede": (13, 83, 4), "Gerberei": (16, 85, 4), "Kaserne": (9, 87, 5), "Waffenlager": (11, 81, 4),
       "Huette": (1, 54, 4), "Lagerplatz": (10, 52, 5), "Markt": (26, 77, 5), "Milchviehhof": (33, 73, 10),
       "Apfelplantage": (32, 72, 10), "Muehle": (34, 74, 3), "Kapelle": (36, 95, 6), "Wachturm": (74, 110, 3),
       "Verteidigungsturm": (75, 111, 4), "Kleines Torhaus NS": (46, 144, 5), "Soeldnerposten": (8, 86, 5),
       "Kornspeicher": (19, 80, 4), "Eisenmine": (5, 90, 4)}
SUCHEN = {}                    # Name -> Suchmitte; wird in main() auf das Lager gesetzt (Lagerplatz, Hoefe)
PAARE = [("Schmiede", "Schmiede"), ("Kaserne", "Kaserne"), ("Schmiede", "Kaserne"), ("Waffenlager", "Waffenlager"),
         ("Verteidigungsturm", "Verteidigungsturm"), ("Huette", "Schmiede")]


def kosten_nullen():
    alt = {}
    for name, (typ, _, _) in ART.items():
        for i in range(5):
            a = KOSTEN + typ * 20 + i * 4
            if a not in alt:
                alt[a] = peek(a)[0]
    for a, v in alt.items():
        if v:
            befehl({"poke": a, "wert": 0}, 0.5, bis="POKE")
    return alt


def kosten_zurueck(alt):
    for a, v in alt.items():
        if v:
            befehl({"poke": a, "wert": v}, 0.5, bis="POKE")


def freie_flaeche(k, groesse, mitte):
    """Linke obere Ecke eines Quadrats groesse x groesse, in dem jedes Feld alle 8 Schritte hat (offen, flach genug),
    moeglichst nah an mitte."""
    offen = {p for p, v in k["f"].items() if v[0] == 0xFF and v[1] == 0}
    best = None
    for (x, y) in offen:
        if all((x + i, y + j) in offen for i in range(groesse) for j in range(groesse)):
            d = abs(x - mitte[0]) + abs(y - mitte[1])
            if best is None or d < best[0]:
                best = (d, (x, y))
    return best[1] if best else None


class Prober:
    def __init__(self, ursprung):
        self.u = ursprung              # linke obere Ecke der Testflaeche
        self.versatz = {}              # Name -> (dx, dy): Grundriss-Ecke minus Bau-Koordinate (aus Schritt 1)
        self.groesse = {}              # Name -> (breit, hoch) GEMESSEN (Kaserne 10x10 mit Exerzierplatz, nicht 5)
        self.ergebnis = {"grundriss": {}, "faelle": []}

    def setze(self, name, x, y):
        """Baut so, dass die linke obere Ecke des Grundrisses auf (x, y) liegt."""
        typ, mapper, b = ART[name]
        dx, dy = self.versatz.get(name, (0, 0))
        befehl({"baue": {"mapper": mapper, "x": x - dx, "y": y - dy, "groesse": b, "richtung": 0}}, 0.8, bis="BAUE")

    def g(self, name):
        return max(self.groesse.get(name, (ART[name][2],) * 2))

    def lesen(self, x0, y0, x1, y1):
        return W.holen(x0, y0, x1, y1)

    def abreissen(self, k, vorher):
        nummern = sorted({v[1] for v in k["f"].values() if v[1] and v[1] not in vorher})
        for n in nummern:
            befehl({"abreissen": {"nr": n}}, 0.6, bis="ABREISSEN")
        warte_ticks(3)
        return nummern

    def grundriss(self, name):
        typ, mapper, b = ART[name]
        rand = max(b, 10) + 6
        vorher = set(E.runde_lesen()[2].keys())          # alle Gebaeudenummern vor dem Bau
        if name in SUCHEN:            # Lagerplatz muss ans Lager, Hoefe brauchen Gruenland: Platzsuche des Spiels
            o = E.baue_schnell(typ, SUCHEN[name][0], SUCHEN[name][1], 45)
            if not o:
                self.ergebnis["grundriss"][name] = {"gebaut": False, "grund": "kein Platz gefunden"}
                print("GRUNDRISS %-20s kein Platz gefunden" % name, flush=True)
                return
            x, y = o
        else:
            x, y = self.u[0] + 6, self.u[1] + 6
            self.setze(name, x, y)
        warte_ticks(4)
        k = self.lesen(x - 6, y - 6, x + rand, y + rand)
        felder = [p for p, v in k["f"].items() if v[1] and v[1] not in vorher]
        if not felder:
            self.ergebnis["grundriss"][name] = {"gebaut": False}
            print("GRUNDRISS %-20s nicht gebaut" % name, flush=True)
            return
        gx0, gy0 = min(p[0] for p in felder), min(p[1] for p in felder)
        gx1, gy1 = max(p[0] for p in felder), max(p[1] for p in felder)
        self.versatz[name] = (gx0 - x, gy0 - y)
        self.groesse[name] = (gx1 - gx0 + 1, gy1 - gy0 + 1)
        boden = erreichbar_vom_rand(k)
        maske = []
        for j in range(gy0, gy1 + 1):
            z = ""
            for i in range(gx0, gx1 + 1):
                v = k["f"][(i, j)]
                if not v[1] or v[1] in vorher:
                    z += "."                                  # gehoert nicht zum Gebaeude
                elif v[0] == 0:
                    z += "#"                                  # gesperrt
                else:
                    # o: vom freien Boden am Fensterrand aus erreichbar (Wegsuche ueber alle erlaubten Schritte);
                    # i: begehbar, aber vom Boden nicht erreichbar (obere Ebene von Turm/Torhaus);
                    # v: kein Schritt fuehrt hinein, nur heraus (Einbahn)
                    von = [1 for bit, (dx, dy) in W.RICHTUNG.items()
                           if (i - dx, j - dy) in k["f"] and k["f"][(i - dx, j - dy)][0] & bit]
                    z += "o" if (i, j) in boden else ("i" if von else "v")
            maske.append(z)
        e = {"gebaut": True, "versatz": self.versatz[name], "groesse": [gx1 - gx0 + 1, gy1 - gy0 + 1], "maske": maske,
             "eckdurchgaenge": len(W.eckdurchgaenge(k)), "einbahn": len(W.einbahn(k))}
        self.ergebnis["grundriss"][name] = e
        W.zeichnen(k, os.path.join(BILDER, "grundriss_%s.png" % name.replace(" ", "_")), W.gebaeude_typen_aus(k, {}),
                   zelle=24, titel="%s: # gesperrt, o vom Boden erreichbar, i begehbar aber vom Boden nicht erreichbar, v nur herunter" % name)
        print("GRUNDRISS %-20s %dx%d Versatz %s  %s" % (name, e["groesse"][0], e["groesse"][1], e["versatz"], " / ".join(maske)),
              flush=True)
        self.abreissen(k, vorher)

    def fall(self, titel, teile, pruefungen):
        """teile = [(name, x, y)] (linke obere Ecken), pruefungen = [(name, start_felder, ziel_felder, box)]."""
        xs = [x for _, x, _ in teile] + [x + self.g(n) for n, x, _ in teile]
        ys = [y for _, _, y in teile] + [y + self.g(n) for n, _, y in teile]
        fen = (min(xs) - 3, min(ys) - 3, max(xs) + 3, max(ys) + 3)
        k0 = self.lesen(*fen)
        vorher = {v[1] for v in k0["f"].values() if v[1]}
        for n, x, y in teile:
            self.setze(n, x, y)
        warte_ticks(4)
        k = self.lesen(*fen)
        # gebaut zaehlt je Teil: steht auf seiner linken oberen Ecke ein NEUES Gebaeude der verlangten Art?
        # (20:30: die Kaserne bringt 3 Exerzierplatz-Gebaeude mit - Nummern zaehlen ergab "4/2" und keine Pruefung)
        da = [n for n, x, y in teile if k["f"].get((x, y), (0, 0, 0, 0, 0, -1))[5] == ART[n][0]
              and k["f"][(x, y)][1] not in vorher]
        e = {"fall": titel, "teile": teile, "gebaut": len(da), "soll": len(teile), "pruefungen": []}
        wege = []
        if len(da) == len(teile):
            for pname, start, ziel, box in pruefungen:
                kurz = None
                for s in start:
                    for z in ziel:
                        w = W.weg(k, s, z, box)
                        if w and (kurz is None or len(w) < len(kurz)):
                            kurz = w
                e["pruefungen"].append({"was": pname, "durch": kurz is not None, "laenge": len(kurz) if kurz else None,
                                        "weg": kurz})
                if kurz:
                    wege.append(kurz)
        e["eckdurchgaenge"] = [[a, b] for a, b, _ in W.eckdurchgaenge(k)]
        self.ergebnis["faelle"].append(e)
        W.zeichnen(k, os.path.join(BILDER, re.sub(r"[^A-Za-z0-9_-]+", "_", titel) + ".png"), W.gebaeude_typen_aus(k, {}),
                   wege=wege, zelle=24, titel=titel)
        print("FALL %-48s gebaut %d/%d  %s" % (titel, len(da), len(teile), "  ".join(
            "%s=%s" % (p["was"], ("JA(%d)" % p["laenge"]) if p["durch"] else "nein") for p in e["pruefungen"])), flush=True)
        self.abreissen(k, vorher)


def erreichbar_vom_rand(k):
    """Alle Felder, die man vom freien Boden am Fensterrand aus ueber erlaubte Schritte erreicht."""
    from collections import deque
    start = [p for p, v in k["f"].items() if v[1] == 0 and v[0] and (p[0] in (k["x0"], k["x1"]) or p[1] in (k["y0"], k["y1"]))]
    gesehen = set(start)
    q = deque(start)
    while q:
        p = q.popleft()
        for bit, (dx, dy) in W.RICHTUNG.items():
            n = (p[0] + dx, p[1] + dy)
            if k["f"][p][0] & bit and n in k["f"] and n not in gesehen:
                gesehen.add(n)
                q.append(n)
    return gesehen


def reihe_felder(x0, x1, y):
    return [(x, y) for x in range(x0, x1 + 1)]


def paare(p):
    ux, uy = p.u[0] + 3, p.u[1] + 3
    for a, b in PAARE:
        ba, bb = p.g(a), p.g(b)
        if ba + bb + 3 > 26:
            print("PAAR %s|%s zu gross fuer die Testflaeche - ausgelassen" % (a, b), flush=True)
            continue
        for g in range(4):                                     # O-W: B rechts von A, Luecke g Felder
            bx = ux + ba + g
            h = max(ba, bb)
            box = (ux, uy - 1, bx + bb - 1, uy + h)
            p.fall("%s|%s O-W Abstand %d" % (a, b, g), [(a, ux, uy), (b, bx, uy)],
                   [("N->S", reihe_felder(ux, bx + bb - 1, uy - 1), reihe_felder(ux, bx + bb - 1, uy + h), box)])
        for g in range(4):                                     # N-S: B unter A
            by = uy + ba + g
            w = max(ba, bb)
            box = (ux - 1, uy, ux + w, by + bb - 1)
            p.fall("%s|%s N-S Abstand %d" % (a, b, g), [(a, ux, uy), (b, ux, by)],
                   [("W->O", [(ux - 1, y) for y in range(uy, by + bb)], [(ux + w, y) for y in range(uy, by + bb)], box)])
        for gx in range(2):                                    # ueber Eck: B rechts unten (SO)
            for gy in range(2):
                bx, by = ux + ba + gx, uy + ba + gy
                box = (ux, uy, bx + bb - 1, by + bb - 1)
                no = [(x, y) for x in range(ux + ba, bx + bb) for y in range(uy, uy + ba) if x >= ux + ba]
                sw = [(x, y) for x in range(ux, ux + ba) for y in range(uy + ba, by + bb)]
                p.fall("%s|%s Eck SO %d-%d" % (a, b, gx, gy), [(a, ux, uy), (b, bx, by)],
                       [("NO->SW", no[:6], sw[:6], box)])
        for gx in range(2):                                    # ueber Eck: B rechts oben (NO)
            for gy in range(2):
                ay = uy + bb + gy                              # A unten links, B oben rechts
                bx, by = ux + ba + gx, uy
                box = (ux, uy, bx + bb - 1, ay + ba - 1)
                nw = [(x, y) for x in range(ux, ux + ba) for y in range(uy, ay)]
                so = [(x, y) for x in range(ux + ba, bx + bb) for y in range(uy + bb, ay + ba)]
                p.fall("%s|%s Eck NO %d-%d" % (a, b, gx, gy), [(a, ux, ay), (b, bx, by)],
                       [("NW->SO", nw[:6], so[:6], box)])


def gruppen(p):
    ux, uy = p.u[0] + 3, p.u[1] + 3
    for name in ("Schmiede", "Kaserne"):
        b = p.g(name)
        for g1 in range(2):                                    # drei in einer Reihe
            for g2 in range(2):
                if 3 * b + g1 + g2 > 27:
                    print("3x %s Reihe %d-%d zu gross fuer die Testflaeche - ausgelassen" % (name, g1, g2), flush=True)
                    continue
                x2, x3 = ux + b + g1, ux + 2 * b + g1 + g2
                box = (ux, uy - 1, x3 + b - 1, uy + b)
                p.fall("3x %s Reihe %d-%d" % (name, g1, g2), [(name, ux, uy), (name, x2, uy), (name, x3, uy)],
                       [("Luecke1 N->S", reihe_felder(ux + b - 1, x2, uy - 1), reihe_felder(ux + b - 1, x2, uy + b),
                         (ux + b - 1, uy - 1, x2, uy + b)),
                        ("Luecke2 N->S", reihe_felder(x2 + b - 1, x3, uy - 1), reihe_felder(x2 + b - 1, x3, uy + b),
                         (x2 + b - 1, uy - 1, x3, uy + b)),
                        ("ganz N->S", reihe_felder(ux, x3 + b - 1, uy - 1), reihe_felder(ux, x3 + b - 1, uy + b), box)])
        for gx in range(3):                                    # vier im Quadrat
            for gy in range(3):
                x2, y2 = ux + b + gx, uy + b + gy
                p.fall("4x %s Quadrat %d-%d" % (name, gx, gy),
                       [(name, ux, uy), (name, x2, uy), (name, ux, y2), (name, x2, y2)],
                       [("N->S Mitte", reihe_felder(ux + b - 1, x2, uy - 1), reihe_felder(ux + b - 1, x2, y2 + b),
                         (ux + b - 1, uy - 1, x2, y2 + b)),
                        ("W->O Mitte", [(ux - 1, y) for y in range(uy + b - 1, y2 + 1)],
                         [(x2 + b, y) for y in range(uy + b - 1, y2 + 1)], (ux - 1, uy + b - 1, x2 + b, y2))])


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    nur, tempo = arg.get("nur", "alle"), int(arg.get("tempo", 100))
    if "paare" in arg:
        PAARE[:] = [tuple(x.split(":")) for x in arg["paare"].split(",")]
    os.makedirs(BILDER, exist_ok=True)
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    alt = kosten_nullen()
    erg = {"kosten_alt": {"0x%08X" % a: v for a, v in alt.items()}}
    try:
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == 10]
        mitte = (teile[0]["x"], teile[0]["y"]) if teile else (165, 111)
        k = W.holen(max(mitte[0] - 70, 0), max(mitte[1] - 70, 0), min(mitte[0] + 70, 399), min(mitte[1] + 70, 399))
        u = freie_flaeche(k, 30, mitte) or freie_flaeche(k, 24, mitte)
        print("Testflaeche ab", u, "(Lager bei %s)" % (mitte,), flush=True)
        if not u:
            raise RuntimeError("keine freie Testflaeche gefunden")
        for n in ("Lagerplatz", "Milchviehhof", "Apfelplantage"):
            SUCHEN[n] = mitte
        p = Prober(u)
        namen = {n for pr in PAARE for n in pr} | ({"Schmiede", "Kaserne"} if nur in ("alle", "gruppen") else set())
        for name in ART:                                   # Grundriss: liefert Versatz und Groesse fuer die Faelle
            if nur == "grundriss" or name in namen:
                p.grundriss(name)
        if "paare" in arg:                                 # z. B. paare=Schmiede:Kaserne,Kaserne:Schmiede
            PAARE[:] = [tuple(x.split(":")) for x in arg["paare"].split(",")]
        if nur in ("alle", "paare"):
            paare(p)
        if nur in ("alle", "gruppen"):
            gruppen(p)
        erg.update(p.ergebnis)
        erg["testflaeche"] = u
    finally:
        kosten_zurueck(alt)
        erg["kosten_zurueck"] = True
        befehl({"pause": True}, 0.5)
        pfad = os.path.join(D, "wege_abstand_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
