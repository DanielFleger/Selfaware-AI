# -*- coding: utf-8 -*-
"""Waechter: erkennt Angriffe auf unsere Wirtschaft und schickt Verteidiger (M15, Daniel 04.10.2026 22:42).

Lagebild (Modulbefehl "lagebild") je Runde. Bedrohung = feindliche Truppe (Besitzer nicht 0 / nicht wir), deren
  - Laufziel hoechstens 6 Felder neben einem unserer Gebaeude liegt (so verrieten sich die Speertraeger, die den
    Kornspeicher abrissen - gemessen 22:41), oder
  - Standort hoechstens 8 Felder neben einem unserer Gebaeude ist.
Abwehr wie der Mensch: Modulbefehl "angriff" (Auswahl = Spielbefehl 16, Angriff = Spielbefehl 36, Art 4).
Gebuendelt (Daniel 22:52): ALLE Verteidiger auf EIN Ziel (das unseren Gebaeuden naechste), erst danach aufs naechste.
Ist der Angreifer noch weiter als 25 Felder von uns, wartet die Gruppe gebuendelt an seinem Laufziel (Abfangen).
Lord (Daniel 22:43: wichtig sind nur seine letzten Lebenspunkte): greift nur ueber 60 % Leben an, unter 50 % zurueck
zum Bergfried-Eingang (Modulbefehl "halten").
Gemessen 22:46: 8 Speertraeger gegen 2 Angreifer - beide tot, keiner von uns verloren.
"""
import math, os
from laden import befehl
from befehl import ABZUG

LAGEBILD = os.path.join(ABZUG, "lagebild.txt")
NAHKAMPF = {24, 25, 26, 27, 28, 37, 55, 71, 73, 75}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
TRUPPE = NAHKAMPF | FERNKAMPF
LORD = 55
LORD_SELBST = 15         # 12.10.: der Lord kaempft nur, wenn Feinde so nah an IHM sind
LORD_FLUCHT = 0.35       # 12.10.: Lord weicht erst unter diesem Lebensanteil (Stellgroesse; vorher 0,5 oder sobald ein Heer kam)
BERGFRIED_EINGANG = (165, 111)

GEBAEUDEDATEI = LAGEBILD.replace("lagebild.txt", "gebaeude.txt")

def lies_gebaeude():
    """Alle Gebaeude aus abzug/gebaeude.txt (schreibt der Modulbefehl lagebild mit): nr -> dict."""
    G = {}
    for z in open(GEBAEUDEDATEI).read().splitlines()[1:]:
        w = z.split()
        if len(w) >= 7:
            G[int(w[0])] = {"besitzer": int(w[1]), "typ": int(w[2]), "x": int(w[3]), "y": int(w[4]), "leben": int(w[5]), "uid": int(w[6]),
                            "erreichbar": int(w[7]) if len(w) >= 8 else 1,
                            # Vorrat im Gebaeude, Hoechstmenge, Verbund (Steinbruch -> sein Steinhaufen Typ 21); seit 05.10. 20:35
                            "vorrat": int(w[8]) if len(w) >= 11 else None, "grenze": int(w[9]) if len(w) >= 11 else None,
                            "verbund": int(w[10]) if len(w) >= 11 else None,
                            # Warenart des Lagerteils (+0x18C, 2 Holz, 4 Stein, 6 Eisen ...); seit 06.10. 20:45
                            "ware": int(w[11]) if len(w) >= 12 else None}
    return G

def lies_lagebild(neu_holen=True):
    if neu_holen:
        befehl({"lagebild": True}, 0.8)
    L = {}
    for z in open(LAGEBILD).read().split("\n")[2:]:
        w = z.split()
        if len(w) >= 16:
            L[int(w[0])] = {"besitzer": int(w[1]), "typ": int(w[2]), "x": int(w[3]), "y": int(w[4]), "leben": int(w[5]),
                            "zustand": int(w[6]), "zielart": int(w[7]), "zieleinheit": int(w[8]), "laufx": int(w[14]), "laufy": int(w[15]),
                            "ladung": int(w[20]) if len(w) >= 22 else 0, "arbeitsplatz": int(w[21]) if len(w) >= 22 else 0,
                            "erreichbar": int(w[22]) if len(w) >= 23 else -1,
                            # Nahkampf (06.10.): wen diese Einheit gerade schlaegt / wie viele sie gerade schlagen
                            "nahziel": int(w[23]) if len(w) >= 25 else -1, "nahangreifer": int(w[24]) if len(w) >= 25 else -1}
    return L

def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def sicherster_ort(L, kandidaten, sp=1):
    """Der Ort aus kandidaten, der am weitesten von jeder feindlichen Truppe weg ist (Schachbrett-Abstand)."""
    feind = [(e["x"], e["y"]) for e in L.values() if e["besitzer"] not in (0, sp) and e["typ"] in TRUPPE]
    if not feind or not kandidaten:
        return kandidaten[0] if kandidaten else None
    return max(kandidaten, key=lambda k: min(schach(k, f) for f in feind))

def hauptheer(L, orte, sp=1, umkreis=35, schwelle=8):
    """Kommt das Hauptheer? = mindestens <schwelle> feindliche Truppen mit Ort oder Laufziel nahe an unseren Orten."""
    n = 0
    for e in L.values():
        if e["besitzer"] in (0, sp) or e["typ"] not in TRUPPE:
            continue
        if any(schach((e["x"], e["y"]), o) <= umkreis or (e["laufx"] > 0 and schach((e["laufx"], e["laufy"]), o) <= umkreis) for o in orte):
            n += 1
    return n >= schwelle, n

class Waechter:
    def __init__(self, sp=1, posten=None):
        self.sp, self.posten = sp, posten
        self.auftrag = {}            # unsere Einheit -> feindliche Einheit
        self.lord_max = None
        self.lord_zurueck = False
        self.besetzt = False
        self.bilanz = {"bedrohungen": set(), "tote_feinde": set(), "eigene_verluste": set()}
        self.bekannt = {}
        self.ziel, self.lauert = None, False

    def stellung(self, L):
        """Zu Spielbeginn: alle Truppen (ohne Lord) an den Posten mitten in der Wirtschaft."""
        eig = [n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] in TRUPPE and e["typ"] != LORD and e["typ"] != 73]
        if eig and self.posten:
            befehl({"halten": {"nr": eig, "x": self.posten[0], "y": self.posten[1]}}, 1.0, bis="HALTEN")
            self.besetzt = True
            return "Stellung: %d Truppen zum Posten %s" % (len(eig), tuple(self.posten))
        return None

    def schritt(self, L, gebaeude, ausgenommen=()):
        """gebaeude: Liste (x, y) unserer Gebaeude; ausgenommen: Einheiten, die der Waechter nicht anfasst
        (z. B. der Angriffstrupp). Gibt Liste von Ereignis-Texten."""
        ereignis = []
        if not self.besetzt:
            t = self.stellung(L)
            if t:
                ereignis.append(t)
        # Bilanz: wer ist seit der letzten Runde verschwunden?
        for n, (bes, typ) in list(self.bekannt.items()):
            if n not in L or L[n]["besitzer"] != bes:
                if bes == self.sp:
                    self.bilanz["eigene_verluste"].add(n)
                elif n in self.bilanz["bedrohungen"]:
                    self.bilanz["tote_feinde"].add(n)
                del self.bekannt[n]
        for n, e in L.items():
            if e["typ"] in TRUPPE and e["besitzer"] not in (0,) and n not in ausgenommen and e["typ"] != 73:
                self.bekannt[n] = (e["besitzer"], e["typ"])
        feinde = {}
        for n, e in L.items():
            if e["besitzer"] in (0, self.sp) or e["typ"] not in TRUPPE:
                continue
            ort, ziel = (e["x"], e["y"]), (e["laufx"], e["laufy"])
            nah_ort = min((schach(ort, g) for g in gebaeude), default=999)
            nah_ziel = min((schach(ziel, g) for g in gebaeude), default=999) if ziel != (0, 0) and ziel[0] > 0 else 999
            if nah_ziel <= 6 or nah_ort <= 8:
                feinde[n] = (min(nah_ort, nah_ziel), e)
        self.bilanz["bedrohungen"] |= set(feinde)
        # Assassinen (73) nie zur Abwehr - wie in stellung(); sonst griff der Waechter frisch Angeworbene ab, bevor der
        # Angriffslenker sie aufnahm (Partie 9c: "Abwehr gebuendelt: alle 16 (22,24,55,73)")
        eigene = {n: e for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] in TRUPPE and e["typ"] != 73
                  and n not in ausgenommen}
        # Lord
        lord = [n for n, e in eigene.items() if e["typ"] == LORD]
        if lord:
            ln = lord[0]; le = eigene[ln]
            self.lord_max = max(self.lord_max or 0, le["leben"])
            anteil = le["leben"] / float(self.lord_max or 1)
            heer, anzahl = hauptheer(L, gebaeude + [BERGFRIED_EINGANG], self.sp)
            # 12.10. (Daniel 11.10. 23:40 "schuetze deine Bogenschuetzen mit dem Lord"): der Lord ist Schild - er weicht
            # NICHT mehr vor einem Heer, nur noch bei wenig Leben (sein Tod verliert die Partie); LORD_FLUCHT ist Stellgroesse
            if anteil < LORD_FLUCHT and not self.lord_zurueck:
                ort = sicherster_ort(L, gebaeude + [BERGFRIED_EINGANG], self.sp)
                befehl({"halten": {"nr": [ln], "x": ort[0], "y": ort[1]}}, 1.0, bis="HALTEN")
                self.lord_zurueck = True; self.auftrag.pop(ln, None)
                ereignis.append("Lord in Sicherheit nach %s (Leben %.0f %%, Feinde nahe %d)" % (tuple(ort), 100 * anteil, anzahl))
            elif self.lord_zurueck and anteil > LORD_FLUCHT + 0.15:
                befehl({"halten": {"los": [ln]}}, 1.0, bis="HALTEN")
                self.lord_zurueck = False
        # 12.10. (Daniel 00:38 "die arabischen Schwertkaempfer reagieren nicht sofort auf die Assassinen, sonst haetten
        # sie die eigenen Bogenschuetzen verteidigt"): wer gerade eine unserer Einheiten angreift (nahangreifer), ist
        # sofort Ziel - auch ausserhalb des Gefahrenkreises, jede Runde neu geprueft
        angreifer = {e.get("nahangreifer") for e in eigene.values() if e.get("nahangreifer")}
        angreifer = {n for n in angreifer if n in L and L[n]["besitzer"] not in (0, self.sp)}
        for n in angreifer:
            feinde.setdefault(n, (0, L[n]))
        fern = [e for e in eigene.values() if e["typ"] in FERNKAMPF]
        if not feinde:
            self.ziel = None
            # Stapeln (Daniel 00:38 "Bogenschuetzen und Schwertkaempfer auf ein Feld, damit diese sie schuetzen"):
            # ohne Gegner stehen die Nahkaempfer auf dem Feld der Fernkaempfer
            if fern:
                mx = int(sum(e["x"] for e in fern) / len(fern)); my = int(sum(e["y"] for e in fern) / len(fern))
                # 12.10. 01:46 (Daniel: "warum sammeln sich jetzt wieder Assassinen in einem Klump?"): Assassinen steuert nur
                # assassinen.py - der Waechter stapelt sie nicht mit
                weg = [n for n, e in eigene.items() if e["typ"] in NAHKAMPF and e["typ"] not in (LORD, 73)
                       and schach((e["x"], e["y"]), (mx, my)) > 2]
                self.stapel_pause = getattr(self, "stapel_pause", 0) - 1
                if weg and self.stapel_pause <= 0:
                    self.stapel_pause = 5               # hoechstens alle 5 Waechter-Runden ein Stapel-Befehl
                    befehl({"angriff": {"einheiten": weg, "lauf": [mx, my]}}, 1.0, bis="ANGRIFF")
                    for n in weg:
                        self.auftrag.pop(n, None)
                    ereignis.append("Stapeln: %d Nahkaempfer auf das Feld der Fernkaempfer (%d,%d)" % (len(weg), mx, my))
            return ereignis
        # 12.10. 01:46 (Daniel: "warum hast du den Lord vorgeschickt?"): der Lord faengt nicht im Feld ab - nur wenn Feinde
        # hoechstens LORD_SELBST Felder neben IHM stehen (er schuetzt sich und die Schuetzen bei ihm). Sein Tod verliert die Partie.
        lord_feind_nah = lambda e: any(schach((e["x"], e["y"]), (f[1]["x"], f[1]["y"])) <= LORD_SELBST for f in feinde.values())
        verfuegbar = [n for n, e in eigene.items()
                      if not (e["typ"] == LORD and (self.lord_zurueck or (self.lord_max and e["leben"] < LORD_FLUCHT * self.lord_max)
                                                    or not lord_feind_nah(e)))]
        if not verfuegbar:
            return ereignis
        gruppe = (sum(eigene[n]["x"] for n in verfuegbar) / len(verfuegbar), sum(eigene[n]["y"] for n in verfuegbar) / len(verfuegbar))
        if angreifer and self.ziel not in angreifer:
            # Angreifer unserer Einheiten zuerst - der, der unseren Fernkaempfern am naechsten ist
            bezug = fern or list(eigene.values())
            self.ziel = min(angreifer, key=lambda n: min(schach((L[n]["x"], L[n]["y"]), (e["x"], e["y"])) for e in bezug))
            self.lauert = False
        elif self.ziel not in feinde:
            # naechstes Ziel: wer unseren Gebaeuden am naechsten ist (Laufziel oder Standort)
            self.ziel = min(feinde, key=lambda n: feinde[n][0])
            self.lauert = False
        fe = feinde[self.ziel][1]
        ort = (fe["x"], fe["y"])
        nah_ort = min((schach(ort, g) for g in gebaeude), default=999)
        if self.ziel not in angreifer and nah_ort > 25 and schach(ort, gruppe) > 12:
            # Angreifer noch weit weg: gebuendelt an seinem Laufziel abfangen (Daniel 22:43: frueh wissen, wo er angreift)
            if not self.lauert and fe["laufx"] > 0:
                befehl({"halten": {"nr": verfuegbar, "x": fe["laufx"], "y": fe["laufy"]}}, 1.0, bis="HALTEN")
                self.lauert = True
                ereignis.append("Abfangen: %d Verteidiger zum Laufziel (%d,%d) von Feind %d (noch %d Felder von uns)" % (
                    len(verfuegbar), fe["laufx"], fe["laufy"], self.ziel, nah_ort))
            return ereignis
        # Fernkaempfer hinter dem Lord (Daniel 23:40): steht ein Fernkaempfer naeher am Ziel als der Lord, laeuft er hinter
        # den Lord zurueck (Punkt 4 Felder hinter dem Lord, vom Ziel weg); er schiesst dann ueber den Lord hinweg
        lord_v = [n for n in verfuegbar if eigene[n]["typ"] == LORD]
        if lord_v:
            lx, ly = eigene[lord_v[0]]["x"], eigene[lord_v[0]]["y"]
            d_lord = schach((lx, ly), ort)
            vorne = [n for n in verfuegbar if eigene[n]["typ"] in FERNKAMPF and schach((eigene[n]["x"], eigene[n]["y"]), ort) < d_lord]
            if vorne and d_lord > 2:
                dx, dy = lx - ort[0], ly - ort[1]
                s = float(max(abs(dx), abs(dy)) or 1)
                hinter = (int(lx + 4 * dx / s), int(ly + 4 * dy / s))
                befehl({"angriff": {"einheiten": vorne, "lauf": [hinter[0], hinter[1]]}}, 1.0, bis="ANGRIFF")
                for n in vorne:
                    self.auftrag.pop(n, None)
                ereignis.append("Schild: %d Fernkaempfer hinter den Lord nach %s (Lord %d Felder vom Ziel)" % (len(vorne), hinter, d_lord))
                verfuegbar = [n for n in verfuegbar if n not in vorne]
        neu = [n for n in verfuegbar if self.auftrag.get(n) != self.ziel]
        if neu:
            befehl({"halten": {"los": verfuegbar}}, 1.0, bis="HALTEN")
            befehl({"angriff": {"einheiten": verfuegbar, "ziel": self.ziel}}, 1.0, bis="ANGRIFF")
            for n in verfuegbar:
                self.auftrag[n] = self.ziel
            self.lauert = False
            ereignis.append("Abwehr gebuendelt: alle %d (%s) gegen Feind %d Typ %d bei (%d,%d)" % (
                len(verfuegbar), ",".join(sorted({str(eigene[n]["typ"]) for n in verfuegbar})), self.ziel, fe["typ"], fe["x"], fe["y"]))
        return ereignis

    def bericht(self):
        b = self.bilanz
        return "Bedrohungen %d, davon tot %d, eigene Truppen verloren %d" % (
            len(b["bedrohungen"]), len(b["tote_feinde"]), len(b["eigene_verluste"]))
