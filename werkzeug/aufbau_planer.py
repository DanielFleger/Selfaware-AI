# -*- coding: utf-8 -*-
"""Aufbauplaner Streitkolben-Kette (Daniel 06.10. 20:29: "maximal effektiver Laufweg fuer 30 Schwertmacher und 30
Lederharnischmacher ... erst 5 von beidem, dann 15, dann 30").

Grundlage (Wissensregister): Laufen 24 Ticks je Feld, gerade = schraeg (G1); Schmied: Rundgang Schmiede -> Lager (Eisen)
-> Waffenlager -> Schmiede, 927 Ticks Arbeit (G3, G4); Gerber: 3 Leder je Kuh in einem Gang zum Waffenlager (G5), Kuh vom
Milchviehhof (G7 offen); Eingang je Bau-Richtung (G10); Werkstaetten sind keine Ecksperre, Waffenlager schon (W3/W4,
ungeprueft); Arbeiter treten zum Abholen auf Lagerteile (W9 widerlegt -> Lagerteile sind Ziel, kein Durchgang).

Rechnet auf der Weg-Ebene des Spiels (wegkarte) plus den geplanten Gebaeuden; setzt gierig eins nach dem anderen an die
Stelle mit dem kuerzesten Gang und prueft nach jedem, dass alle Eingaenge erreichbar bleiben. Ergebnis ist ein PLAN
(ungeprueft), das Spiel bestaetigt ihn erst beim Bauen und Messen.
"""
import os
import sys
from collections import deque

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import wegkarte as W

TICKS_JE_FELD = 24                  # G1
ARBEIT_SCHMIED = 927                # G3
EINGANG = {0: (2, 4), 2: (-1, 2), 4: (1, -1), 6: (4, 1)}     # G10, 4x4-Gebaeude
LAGER, WAFFENLAGER, SCHMIEDE, GERBEREI = 10, 11, 13, 16


class Plan:
    def __init__(self, k, ausgeschlossene_flaechen=()):
        self.k = k
        self.ausgeschlossene_flaechen = tuple(tuple(r) for r in ausgeschlossene_flaechen)
        self.belegt = {}             # Feld -> geplante Art
        self.eingaenge = []          # (art, feld)
        self.bauten = []             # (art, x, y, richtung, eingang)

    # --- Gelaende -------------------------------------------------------------------------------------------------
    def boden(self, p):
        """Begehbarer Boden: in der Weg-Ebene begehbar, kein Lagerteil, nicht geplant belegt."""
        v = self.k["f"].get(p)
        return v is not None and v[0] != 0 and v[5] != LAGER and p not in self.belegt

    def eckensperre(self, p):
        if p in self.belegt:
            return self.belegt[p] in W.ECKSPERRE
        v = self.k["f"].get(p)
        return v is not None and v[0] == 0 and (v[5] in W.ECKSPERRE or v[3] & 0x30)

    def schritte(self, p):
        """Geplante Gebaeude nehmen Wege nur weg, nie hinzu: erlaubt ist ein Schritt, wenn die Weg-Ebene ihn heute
        erlaubt, das Ziel freier Boden bleibt und schraeg nicht zwei Ecksperren (auch geplante Waffenlager) daneben sind."""
        v = self.k["f"][p]
        for bit, (dx, dy) in W.RICHTUNG.items():
            n = (p[0] + dx, p[1] + dy)
            if not v[0] & bit or not self.boden(n):
                continue
            if dx and dy and self.eckensperre((p[0] + dx, p[1])) and self.eckensperre((p[0], p[1] + dy)):
                continue
            yield n

    def abstand(self, start):
        """Felder-Abstand von start (Feld oder Liste) zu allem Boden."""
        q = deque(start if isinstance(start, list) else [start])
        d = {p: 0 for p in q}
        while q:
            p = q.popleft()
            for n in self.schritte(p):
                if n not in d:
                    d[n] = d[p] + 1
                    q.append(n)
        return d

    def lager_abstand(self):
        """Abstand jedes Bodenfelds zum naechsten Lagerteil (ein Schritt auf das Teil gehoert dazu)."""
        teile = [p for p, v in self.k["f"].items() if v[5] == LAGER]
        start = {n for t in teile for n in ((t[0] + dx, t[1] + dy) for dx, dy in W.RICHTUNG.values()) if self.boden(n)}
        d = self.abstand(sorted(start))
        return {p: v + 1 for p, v in d.items()}

    # --- Bauen ----------------------------------------------------------------------------------------------------
    def frei(self, x, y, b=4):
        return all(self.boden((x + i, y + j)) and self.k["f"][(x + i, y + j)][0] == 0xFF
                   and (x + i, y + j) not in [e for _, e in self.eingaenge] for i in range(b) for j in range(b))

    def setze(self, art, x, y, r, b=4):
        for i in range(b):
            for j in range(b):
                self.belegt[(x + i, y + j)] = art
        e = (x + EINGANG[r][0], y + EINGANG[r][1])
        self.eingaenge.append((art, e))
        self.bauten.append((art, x, y, r, e))
        return e

    def zuruecknehmen(self):
        art, x, y, r, e = self.bauten.pop()
        self.eingaenge.pop()
        for i in range(4):
            for j in range(4):
                self.belegt.pop((x + i, y + j), None)

    def alle_erreichbar(self, ziel):
        d = self.abstand(ziel)
        return all(e in d for _, e in self.eingaenge)

    def kandidaten(self, mitte, r_max):
        for x in range(mitte[0] - r_max, mitte[0] + r_max):
            for y in range(mitte[1] - r_max, mitte[1] + r_max):
                # Ein vom echten Spiel wiederholt abgelehnter 4x4-Platz bleibt auch nach dem Neulesen der Wegkarte
                # scheinbar frei. Jede spaetere 4x4-Flaeche, die ihn ueberlappt, wird deshalb fuer diese Partie
                # ausgeschlossen; nur den identischen Anker zu sperren verschiebt dieselbe Schleife um ein Feld.
                if any(x <= r[2] and x + 3 >= r[0] and y <= r[3] and y + 3 >= r[1]
                       for r in self.ausgeschlossene_flaechen):
                    continue
                # Gedrehte Wirtschaftsgebaeude sahen in echten Partien teils nur als Geruest/Fragment aus. Solange
                # nicht jede Drehung visuell und mit echtem Lieferweg bestaetigt ist, gilt Richtung 0 als einzige
                # sichere gemeinsame Regel. Der kuerzeste Plan darf keine kaputte Darstellung erkaufen.
                for r in (0,):
                    if self.frei(x, y):
                        e = (x + EINGANG[r][0], y + EINGANG[r][1])
                        if self.boden(e) and all(not (x <= e2[0] < x + 4 and y <= e2[1] < y + 4) for _, e2 in self.eingaenge):
                            yield x, y, r, e


def hoftore(x, y):
    """Tore im Zaun eines Milchviehhofs (10x10, Grundriss 20:28): Mitte jeder Seite, je 2 Felder. Hier holt der Gerber
    die Kuh (gemessen 20:33: Gerber stand bei (x, y+5))."""
    return [(x + 4, y), (x + 5, y), (x, y + 4), (x, y + 5), (x + 9, y + 4), (x + 9, y + 5), (x + 4, y + 9), (x + 5, y + 9)]


def kartenrahmen(anker, hoefe=(), rand=35):
    """Kartenausschnitt fuer die gemeinsame Waffenproduktion.

    Jeder an den Planer uebergebene Hof muss samt Zaun und Rand wirklich in der Wegkarte liegen. Ein fester Ausschnitt
    nur um das Vorratslager machte eine nichtleere Hofliste mit null sichtbaren Hoftoren und verwarf dadurch jeden
    Waffenlagerplatz. Die Spielkarte selbst begrenzt den schlimmsten Fall fest auf 400x400 Felder.
    """
    punkte = [tuple(anker)] + [(x, y) for x, y in hoefe] + [(x + 9, y + 9) for x, y in hoefe]
    return (max(min(x for x, _y in punkte) - rand, 0),
            max(min(y for _x, y in punkte) - rand, 0),
            min(max(x for x, _y in punkte) + rand, 399),
            min(max(y for _x, y in punkte) + rand, 399))


def platzablehnung_merken(speicher, ort, grund, grenze=2):
    """Nur echte, wiederholte Platzablehnungen zaehlen; Rohstoffmangel und Laufspuren sperren keinen Bauplatz."""
    if grund != "platz":
        return False
    ort = tuple(ort)
    speicher[ort] = speicher.get(ort, 0) + 1
    return speicher[ort] >= grenze


def plane(k, n_schmiede, n_gerber, eisen_teil=None, hoefe=(), r_max=16, waffenlager_eingang=None,
          vorhandene_eingaenge=(), ausgeschlossene_flaechen=()):
    """Runde 2 (06.10. 20:47, nach A11/A12): Rundgang Schmied = Eingang -> Waffenlager -> EISENTEIL -> Eingang;
    Gerber je 3 Leder = 2 x Weg zum naechsten Hoftor + 2 x Weg zum Waffenlager. eisen_teil = Lagerteil-Nummer mit Eisen
    (Lagebild, Spalte ware), hoefe = [(x, y)] der Milchviehhoefe. Gibt (plan, bericht)."""
    p = Plan(k, ausgeschlossene_flaechen)
    alle_teile = [q for q, v in k["f"].items() if v[5] == LAGER]
    eisen = [q for q, v in k["f"].items() if v[5] == LAGER and (eisen_teil is None or v[1] == eisen_teil)] or alle_teile
    mitte = (sum(q[0] for q in eisen) // len(eisen), sum(q[1] for q in eisen) // len(eisen))
    tore = [t for h in hoefe for t in hoftore(*h)]
    sichtbare_tore = [t for t in tore if p.boden(t)]
    if tore and not sichtbare_tore:
        raise RuntimeError("kein Hoftor im Kartenausschnitt; kartenrahmen() mit allen gebauten Hoefen verwenden")
    bericht = {"mitte": mitte, "eisen_teil": eisen_teil, "tore": tore, "schmiede": [], "gerber": []}

    def zum_eisen():                        # Abstand jedes Bodenfelds zum Eisenteil (ein Schritt auf das Teil dazu)
        start = {n for t in eisen for n in ((t[0] + dx, t[1] + dy) for dx, dy in W.RICHTUNG.values()) if p.boden(n)}
        return {q: v + 1 for q, v in p.abstand(sorted(start)).items()}

    # 1. Ein einziges Waffenlager fuer beide Ketten. Drei echte Gegenlaeufe (09.10.) fanden nach dem ersten Lager
    # selbst im 65x65-Hofbereich keinen einzigen Bauplatz fuer ein zweites: das Spiel laesst nur eines zu. Das eine
    # Lager gehoert deshalb an den Vorrats-/Eisenanker: Schmiede brauchen pro Keule sowohl Eisen als auch Waffenlager,
    # waehrend ein Gerber drei Leder je Kuhgang traegt. Ein gemeinsamer Mittelpunkt machte beide Schmiedwege um rund
    # 40 Felder laenger und ist fuer das Zeitrennen schlechter; der Gerber traegt bewusst den laengeren Nebenweg.
    de = zum_eisen()
    dt0 = p.abstand(sichtbare_tore) if tore else {}
    if waffenlager_eingang is not None:
        # Zweite Planungsstufe: Das echte, bereits gebaute Lager ist der gemeinsame Anker. Es wird nur als Ziel/Eingang
        # eingetragen, nicht noch einmal gebaut. Die Wegkarte selbst enthaelt seinen blockierten Grundriss bereits.
        we = tuple(waffenlager_eingang)
        if not p.boden(we) or we not in de or (tore and we not in dt0):
            raise RuntimeError("vorhandenes Waffenlager ist fuer die neue Werkstattstufe nicht erreichbar")
        p.eingaenge.append((WAFFENLAGER, we))
        bericht["waffenlager"] = {"bestehend": True, "eingang": we, "zum_eisen": de[we],
                                    "zum_hof": dt0.get(we)}
    else:
        mitte_w, r_w = mitte, 16
        best = None
        for x, y, r, e in p.kandidaten(mitte_w, r_w):
            if e not in de or (tore and e not in dt0):
                continue
            hofweg = dt0.get(e, 0)
            # Vorratsweg ist die erste Ordnung; der Hofweg entscheidet nur zwischen gleich guten Lagerplaetzen.
            kandidat = (de[e], hofweg, x, y, r)
            if best is None or kandidat < best:
                best = kandidat
        if best is None:
            raise RuntimeError("kein Platz fuer das Waffenlager")
        we = p.setze(WAFFENLAGER, best[2], best[3], best[4])
        bericht["waffenlager"] = {"ort": best[2:4], "richtung": best[4], "eingang": we,
                                    "zum_eisen": de[we], "zum_hof": dt0.get(we)}

    # Neuplanung darf Wege bereits gebauter Werkstaetten nicht opfern. Ihre echten Richtung-0-Eingaenge werden wie
    # geplante Eingange in jede Erreichbarkeitspruefung aufgenommen, ohne die Gebaeude erneut zu bauen.
    for art, e in vorhandene_eingaenge:
        e = tuple(e)
        if not p.boden(e):
            raise RuntimeError("vorhandener Werkstatt-Eingang %s ist blockiert" % (e,))
        p.eingaenge.append((art, e))

    def pruefe(ziel_eisen):
        dw2, de2 = p.abstand(we), zum_eisen()
        return all(e2 in dw2 for _, e2 in p.eingaenge) and all(e2 in de2 for a2, e2 in p.eingaenge if a2 == SCHMIEDE)

    def setze_schmiede():
        de, dw = zum_eisen(), p.abstand(we)
        w_zu_eisen = de.get(we, 999)
        best = None
        for x, y, r, e in p.kandidaten(mitte, r_max):
            if e not in de or e not in dw:
                continue
            gang = dw[e] + w_zu_eisen + de[e]
            if best is None or gang < best[0]:
                p.setze(SCHMIEDE, x, y, r)
                ok = pruefe(True)
                p.zuruecknehmen()
                if ok:
                    best = (gang, x, y, r)
        if best is None:
            bericht["schmiede"].append({"fehlt": "kein Platz"})
            return
        e = p.setze(SCHMIEDE, best[1], best[2], best[3])
        bericht["schmiede"].append({"ort": best[1:3], "richtung": best[3], "eingang": e, "gang_felder": best[0],
                                    "zyklus_ticks": ARBEIT_SCHMIED + best[0] * TICKS_JE_FELD})

    def setze_gerber():
        dw = p.abstand(we)
        dt = p.abstand(sichtbare_tore) if tore else {}
        best = None
        mitte_g = mitte if not tore else ((we[0] + sum(t[0] for t in tore) // len(tore)) // 2,
                                          (we[1] + sum(t[1] for t in tore) // len(tore)) // 2)
        for x, y, r, e in p.kandidaten(mitte_g, r_max + 14):
            if e not in dw or (tore and e not in dt):
                continue
            gang = 2 * dw[e] + (2 * dt[e] if tore else 0)
            if best is None or gang < best[0]:
                p.setze(GERBEREI, x, y, r)
                ok = pruefe(False)
                p.zuruecknehmen()
                if ok:
                    best = (gang, x, y, r)
        if best is None:
            bericht["gerber"].append({"fehlt": "kein Platz"})
            return
        e = p.setze(GERBEREI, best[1], best[2], best[3])
        bericht["gerber"].append({"ort": best[1:3], "richtung": best[3], "eingang": e, "gang_felder": best[0],
                                  "zyklus_ticks": 1555 + best[0] * TICKS_JE_FELD})

    # Platz UND Baufolge gleichrangig vergeben: Leder beginnt wegen Kuhweg und laengerer Arbeitszeit zuerst, danach
    # wechseln beide Ketten. Uebrige Betriebe der groesseren Seite folgen erst am Ende.
    for i in range(max(n_schmiede, n_gerber)):
        if i < n_gerber:
            setze_gerber()
        if i < n_schmiede:
            setze_schmiede()
    return p, bericht


def zeichne_plan(plan, pfad, titel=""):
    """Plan als Bild: geplante Gebaeude als belegte Felder (eigene Nummern ab 900), Eingaenge als begehbare Felder."""
    k = dict(plan.k)
    f = dict(k["f"])
    nummer = {}
    for i, (art, x, y, r, e) in enumerate(plan.bauten):
        for a in range(4):
            for b in range(4):
                q = (x + a, y + b)
                if q in f:
                    v = f[q]
                    f[q] = (0, 900 + i, v[2], v[3] | 0x400, v[4], art)
    k["f"] = f
    x0 = min(x for _, x, _, _, _ in plan.bauten) - 6
    y0 = min(y for _, _, y, _, _ in plan.bauten) - 6
    x1 = max(x for _, x, _, _, _ in plan.bauten) + 10
    y1 = max(y for _, _, y, _, _ in plan.bauten) + 10
    k.update(x0=max(x0, k["x0"]), y0=max(y0, k["y0"]), x1=min(x1, k["x1"]), y1=min(y1, k["y1"]))
    k["f"] = {q: v for q, v in f.items() if k["x0"] <= q[0] <= k["x1"] and k["y0"] <= q[1] <= k["y1"]}
    return W.zeichnen(k, pfad, W.gebaeude_typen_aus(k, {}), zelle=20, titel=titel)


if __name__ == "__main__":
    import glob
    import json
    pfad = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(HIER, "..", "daten", "arbeitsgang_*_wegkarte.txt")))[-1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    k = W.lesen(pfad)
    # geplante/vorhandene Werkstaetten der Messpartie aus der Karte nehmen: nur Lager bleiben als Bestand
    plan, bericht = plane(k, n, n)
    w = bericht["waffenlager"]
    print("Waffenlager", w["ort"], "Richtung", w["richtung"], "Eingang", w["eingang"], "zum Lager", w["zum_lager"], "Felder")
    for s2 in bericht["schmiede"]:
        print("Schmiede", s2.get("ort"), "R", s2.get("richtung"), "Rundgang", s2.get("gang_felder"), "Felder =",
              s2.get("gang_ticks"), "Ticks, Zyklus", s2.get("zyklus_ticks"))
    for s2 in bericht["gerber"]:
        print("Gerberei", s2.get("ort"), "R", s2.get("richtung"), "Gang", s2.get("gang_felder"), "Felder =", s2.get("gang_ticks"), "Ticks")
    print(zeichne_plan(plan, os.path.join(HIER, "..", "daten", "plan_%d_%d.png" % (n, n)), "Plan %d Schmieden + %d Gerbereien" % (n, n)))
