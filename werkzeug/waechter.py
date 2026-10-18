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
import gefecht

LAGEBILD = os.path.join(ABZUG, "lagebild.txt")
NAHKAMPF = {24, 25, 26, 27, 28, 37, 55, 71, 73, 75}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
TRUPPE = NAHKAMPF | FERNKAMPF
LORD = 55
LORD_SELBST = 15         # 12.10.: der Lord kaempft nur, wenn Feinde so nah an IHM sind
LORD_FLUCHT = 0.35       # 12.10.: Lord weicht erst unter diesem Lebensanteil (Stellgroesse; vorher 0,5 oder sobald ein Heer kam)
ANGREIFER_R = 40         # 19.10.: Angreifer unserer Einheiten zaehlen nur bis hierhin von unseren Gebaeuden (nicht draussen)
GRUPPE_R = 10            # 19.10.: feindliche Einheiten so nah beieinander (Kette) = eine Gruppe fuer die Gefechtsbewertung
WERTUNG_RUNDEN = 3       # 19.10.: Gefechtsbewertung neu je so viele Waechter-Runden (oder bei neuem Ziel)
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
            # 18.10. (Gegenpruefung, belegt in 1017h-j: ~770 Assassinen-Runden Modell 0 bei ~360.000 Leben Verlust): sicht.py
            # braucht "nr" und "gruppe" - ohne sie hatten alle eigenen Einheiten Nummer 0 und es gab nie Verfolger
            L[int(w[0])] = {"nr": int(w[0]), "gruppe": int(w[18]) if len(w) >= 19 else 0,
                            "besitzer": int(w[1]), "typ": int(w[2]), "x": int(w[3]), "y": int(w[4]), "leben": int(w[5]),
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
        self.verzicht = None         # 19.10.: Ziel, gegen das die Gefechtsbewertung zuletzt "lohnt nicht" ergab
        self.zurueck = None          # 19.10.: (Ziel, Schuetzen), die zuletzt aus dem Nahkampf herausgehalten wurden

    def stellung(self, L):
        """Zu Spielbeginn: alle Truppen (ohne Lord) an den Posten mitten in der Wirtschaft."""
        eig = [n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] in TRUPPE and e["typ"] != LORD and e["typ"] != 73]
        if eig and self.posten:
            befehl({"halten": {"nr": eig, "x": self.posten[0], "y": self.posten[1]}}, 1.0, bis="HALTEN")
            self.besetzt = True
            return "Stellung: %d Truppen zum Posten %s" % (len(eig), tuple(self.posten))
        return None

    def schritt(self, L, gebaeude, ausgenommen=(), reserve=()):
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
                  and n not in ausgenommen and n not in reserve}
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
        # 19.10. (1019b: vier feindliche Assassinen toeteten 7 arabische Bogen, waehrend alle 28 Verteidiger einem Bogen 50
        # Felder weiter nachliefen; einmal "Abwehr gegen Feind 2 Typ 13", einen Arbeiter): "nahangreifer" ist die ZAHL der
        # Angreifer, keine Nummer - Feind 2 war "2 greifen an". Angreifer sind die feindlichen Einheiten, deren nahziel
        # (Nahkampf) oder zieleinheit (Schuss) eine unserer Einheiten in unserem Gebiet ist (Truppen des Waechters,
        # Arbeiter, Bauern - nicht Assassinen oder Feldzug draussen) und die hoechstens ANGREIFER_R Felder von uns stehen
        geschuetzt = set(eigene) | {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] not in TRUPPE}
        angreifer = {n for n, e in L.items() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE
                     and (e.get("nahziel") in geschuetzt or e.get("zieleinheit") in geschuetzt)
                     and min((schach((e["x"], e["y"]), g) for g in gebaeude), default=0) <= ANGREIFER_R}
        for n in angreifer:
            feinde.setdefault(n, (0, L[n]))
        fern = [e for e in eigene.values() if e["typ"] in FERNKAMPF]
        if not feinde:
            self.ziel = None
            for n in reserve:                    # 19.10.: Reserve (Feldzug beim Sammeln) wieder frei fuer den Feldzug
                self.auftrag.pop(n, None)
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
        # 19.10. (Daniel, Bild 1019b: Feinde zerstoerten unsere Felder, unsere Truppen standen daneben): bei einer Bedrohung
        # zaehlt die Reserve mit (Streitkolben des Feldzugs, solange er sammelt) - ob sie kaempft, entscheidet die Bewertung
        eigene = dict(eigene)
        eigene.update({n: L[n] for n in reserve if n in L and L[n]["besitzer"] == self.sp})
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
        # 19.10. (Daniel, 1019b: "die lassen sich einfach angreifen ohne Grund und koennen nicht evaluieren, wann ein Counter
        # sich lohnt - jede Sekunde Zoegerung kostet Leben"): Gefecht vorher durchrechnen (gefecht.py, Editor-Duelle) - nur
        # angreifen, wenn die Gruppe faellt und genug von uns bleibt; sonst Schuetzen zu den Nahkaempfern an den Bergfried
        lohnt, text, einsatz = self._bewerten(L, eigene, verfuegbar)
        if not lohnt:
            if self.verzicht != self.ziel:
                self.verzicht = self.ziel
                sammel = BERGFRIED_EINGANG
                # die Reserve (Feldzug) bleibt an ihrem Sammelpunkt - der Feldzug fuehrt sie, sobald sie frei ist
                eigen_v = [n for n in verfuegbar if n not in reserve]
                for n in verfuegbar:
                    self.auftrag.pop(n, None)
                if eigen_v:
                    befehl({"halten": {"los": eigen_v}}, 1.0, bis="HALTEN")
                    befehl({"angriff": {"einheiten": eigen_v, "lauf": [sammel[0], sammel[1]]}}, 1.0, bis="ANGRIFF")
                ereignis.append("ABWEHR VERZICHTET gegen Feind %d Typ %d bei (%d,%d): %s - %d sammeln am Bergfried %s" % (
                    self.ziel, fe["typ"], fe["x"], fe["y"], text, len(eigen_v), tuple(sammel)))
            return ereignis
        self.verzicht = None
        # 19.10.: nur die Nahkaempfer, wenn das mehr von uns uebrig laesst - die Schuetzen bleiben dann aus dem Nahkampf
        # (1019b: 7 arab. Bogen starben im Nahkampf mit 4 Assassinen); stehen Feinde der Gruppe nah an ihnen, weichen sie zurueck
        raus = [n for n in verfuegbar if n not in einsatz]
        if raus and self.zurueck != (self.ziel, tuple(sorted(raus))):
            gruppe_orte = [(L[k]["x"], L[k]["y"]) for k in getattr(self, "_gruppe", ()) if k in L]
            bedroht = [n for n in raus if any(schach((eigene[n]["x"], eigene[n]["y"]), q) <= 12 for q in gruppe_orte)]
            if bedroht:
                befehl({"angriff": {"einheiten": bedroht, "lauf": [BERGFRIED_EINGANG[0], BERGFRIED_EINGANG[1]]}}, 1.0, bis="ANGRIFF")
                for n in bedroht:
                    self.auftrag.pop(n, None)
                ereignis.append("Schuetzen raus: %d weichen zum Bergfried, die Nahkaempfer uebernehmen" % len(bedroht))
            self.zurueck = (self.ziel, tuple(sorted(raus)))
        verfuegbar = list(einsatz)
        neu = [n for n in verfuegbar if self.auftrag.get(n) != self.ziel]
        if neu:
            befehl({"halten": {"los": verfuegbar}}, 1.0, bis="HALTEN")
            befehl({"angriff": {"einheiten": verfuegbar, "ziel": self.ziel}}, 1.0, bis="ANGRIFF")
            for n in verfuegbar:
                self.auftrag[n] = self.ziel
            self.lauert = False
            ereignis.append("Abwehr gebuendelt: alle %d (%s) gegen Feind %d Typ %d bei (%d,%d) - %s" % (
                len(verfuegbar), ",".join(sorted({str(eigene[n]["typ"]) for n in verfuegbar})), self.ziel, fe["typ"], fe["x"], fe["y"],
                text))
        return ereignis

    def _bewerten(self, L, eigene, verfuegbar):
        """19.10.: (lohnt, Text) fuer den Angriff aller verfuegbaren auf die Gruppe um self.ziel - die Gruppe = feindliche
        Truppen in einer Kette von je hoechstens GRUPPE_R Feldern um das Ziel; dazu feindliche Schuetzen, deren Reichweite
        den Kampfplatz erreicht (sie stehen und schiessen mit). Neu je WERTUNG_RUNDEN Runden oder bei neuem Ziel."""
        self.runde_w = getattr(self, "runde_w", 0) + 1
        alt = getattr(self, "_wertung", None)
        if alt and alt[0] == self.ziel and self.runde_w - alt[1] < WERTUNG_RUNDEN:
            return alt[2], alt[3], [n for n in alt[4] if n in verfuegbar]
        feind = {n: e for n, e in L.items() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE and e["typ"] != LORD}
        gruppe, offen = {self.ziel}, [self.ziel]
        while offen:
            k = offen.pop()
            for n, e in feind.items():
                if n not in gruppe and schach((e["x"], e["y"]), (L[k]["x"], L[k]["y"])) <= GRUPPE_R:
                    gruppe.add(n); offen.append(n)
        mitte = (L[self.ziel]["x"], L[self.ziel]["y"])
        helfer = {n for n, e in feind.items() if n not in gruppe and e["typ"] in gefecht.FERN_REICH
                  and schach((e["x"], e["y"]), mitte) <= gefecht.FERN_REICH[e["typ"]]}
        # die Feinde kaempfen dort, wo sie sind (sie zerstoeren unsere Gebaeude, laufen uns nicht entgegen) - unsere muessen hin
        # (Pruefung 5: mit Entgegenlaufen traf sich der Sklave 130 Felder weit draussen auf halbem Weg mit uns)
        sie = [dict(typ=L[n]["typ"], leben=L[n]["leben"], x=L[n]["x"], y=L[n]["y"], steht=True) for n in gruppe | helfer]
        self._gruppe = gruppe
        # zwei Moeglichkeiten: alle verfuegbaren, oder nur die Nahkaempfer (Schuetzen bleiben draussen) - die mit mehr Rest
        nahk = [n for n in verfuegbar if eigene[n]["typ"] not in FERNKAMPF]
        wahl = [("alle", list(verfuegbar))] + ([("nur Nahkampf", nahk)] if nahk and len(nahk) < len(verfuegbar) else [])
        beste = None
        for name, ns in wahl:
            wir = [dict(typ=eigene[n]["typ"], leben=eigene[n]["leben"], x=eigene[n]["x"], y=eigene[n]["y"]) for n in ns]
            try:
                lohnt, text = gefecht.bewerte(wir, sie)
                anteil = float(text.rsplit("bleiben ", 1)[1].split(" ")[0]) if "bleiben " in text else 0.0
            except Exception as ex:              # ohne Messdaten nicht blockieren - dann wie bisher angreifen
                lohnt, text, anteil = True, "Bewertung fehlgeschlagen (%s) - greift an" % ex, 0.0
            if beste is None or (lohnt, anteil) > (beste[0], beste[3]):
                beste = (lohnt, "%s: %s" % (name, text), ns, anteil)
        lohnt, text, einsatz = beste[0], beste[1], beste[2]
        text = "Gruppe %d + %d Schuetzen am Rand; %s" % (len(gruppe), len(helfer), text)
        self._wertung = (self.ziel, self.runde_w, lohnt, text, einsatz)
        return lohnt, text, einsatz

    def bericht(self):
        b = self.bilanz
        return "Bedrohungen %d, davon tot %d, eigene Truppen verloren %d" % (
            len(b["bedrohungen"]), len(b["tote_feinde"]), len(b["eigene_verluste"]))
