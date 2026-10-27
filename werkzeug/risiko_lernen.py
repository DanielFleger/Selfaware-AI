# -*- coding: utf-8 -*-
"""Lernende Eichung des Assassinen-Risikos (B-278, Meta 4 Vorhersage-Tagebuch; Daniel 27.10. 23:27 "lernender Ansatz ...
bitte kombinieren"; Plan_Assassinen_Risiko.md).

Jeder Angriff einer Assassine (ZIELWAHL bis das Ziel weg ist, sie es aufgibt oder stirbt) traegt Vorhersage (Weg + Ziel, OHNE
Eichung) und echten Lebensverlust ein. Angriffe, in denen sie im Nahkampf stand (nahangreifer > 0), zaehlen nicht - das Modell
rechnet nur Beschuss. KALIB = (echt + START x PRIOR) / (vorhergesagt + PRIOR): der Startwert 0,33 (B-204, gemessen 1017h-j)
wiegt wie PRIOR Leben Vorhersage und wird von jeder Partie verschoben. Gespeichert je Lernprofil (SHC_LEARNING_DIR) wie
verlust_raten.json. Rueckweg: assassinen.KALIB_LERNEN = False."""
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
START = 0.33
PRIOR = 30000.0              # Vorhersage-Leben, mit denen der Startwert zaehlt (~3 typische Angriffe) - Startwert, UNGEMESSEN
GRENZEN = (0.02, 2.0)        # die Eichung bleibt in diesem Band (ein einzelner Ausreisser kippt sie nicht ins Absurde)
# Frage-Agent 23:32 (gelb, Frage 2): nach ENTDECKT wird das Ziel sofort verworfen, Treffer kommen 64-170 Takte spaeter (L81) -
# ein Angriff bleibt darum NACHLAUF Takte nach seinem Ende offen; der Verlust auf der Flucht gehoert zu ihm
NACHLAUF = 200
# B-279 (Partie 001807: KALIB fiel von 0,33 auf 0,03 - "vorhergesagt 20.718, echt 0" bei Assassinen, die ihr Ziel unterwegs
# wechselten und nie dort waren): ein Angriff zaehlt nur, wenn die Assassine bis ANKOMMEN Felder ans Ziel kam oder starb
ANKOMMEN = 6
# Partie 002852: der neue Prozess lud die Datei, die der alte (vor B-279, falsche Zaehlung) um 00:25 neu geschrieben hatte -
# KALIB 0,047 statt 0,33. Gelesen wird nur eine Datei mit dieser FASSUNG; aeltere Staende bleiben liegen und werden uebergangen
FASSUNG = 2


def pfad():
    """Nur im Lernprofil der Partie (SHC_LEARNING_DIR); ohne Profil (Pruefungen) lernt sie nur im Speicher."""
    d = os.environ.get("SHC_LEARNING_DIR")
    return os.path.join(d, "assassinen_eichung.json") if d else None


class Eichung:
    def __init__(self, datei=None):
        self.datei = datei or pfad()
        self.vorher, self.echt, self.zahl, self.nahkampf = 0.0, 0.0, 0, 0
        try:
            d = json.load(open(self.datei, encoding="utf-8")) if self.datei else {}
            if d.get("fassung") != FASSUNG:
                raise KeyError("fassung")
            self.vorher, self.echt, self.zahl = float(d["vorhergesagt"]), float(d["echt"]), int(d["angriffe"])
        except (OSError, ValueError, KeyError, TypeError):
            pass
        self.offen = {}          # Einheit -> {"ziel", "vorher", "leben", "t", "nah"}
        self.partie = [0, 0.0, 0.0]

    @property
    def kalib(self):
        k = (self.echt + START * PRIOR) / (self.vorher + PRIOR)
        return min(GRENZEN[1], max(GRENZEN[0], k))

    def start(self, n, ziel, vorhersage, leben, t, ziel_ort=None):
        """Bei ZIELWAHL: Vorhersage ohne Eichung (Weg + Ziel, Leben), Leben jetzt. Ein noch offener Angriff derselben Einheit
        wird vorher geschlossen."""
        aus = self._schliessen(n, t) if n in self.offen else []
        self.offen[n] = {"ziel": ziel, "vorher": float(vorhersage), "leben": float(leben), "t": t, "nah": False, "ende": None,
                         "ort": ziel_ort, "da": ziel_ort is None}
        return aus

    def runde(self, L, ziele, t):
        """Jede Runde: ziele = {Einheit: jetziges Ziel}. Ein Angriff endet, wenn die Einheit tot ist, oder NACHLAUF Takte nachdem
        ihr Ziel weg/anders ist. Gibt Meldungen."""
        aus = []
        for n, a in list(self.offen.items()):
            e = L.get(n)
            tot = e is None or e.get("leben", 0) <= 0
            if tot:
                aus += self._schliessen(n, t, tot=True)
                continue
            a["leben_jetzt"] = float(e.get("leben", a["leben"]))
            if a["ort"] is not None and max(abs(e["x"] - a["ort"][0]), abs(e["y"] - a["ort"][1])) <= ANKOMMEN:
                a["da"] = True
            if (e.get("nahangreifer") or 0) > 0:
                a["nah"] = True
            if ziele.get(n) == a["ziel"]:
                a["ende"] = None
                continue
            if a["ende"] is None:
                a["ende"] = t
            if t - a["ende"] >= NACHLAUF:
                aus += self._schliessen(n, t)
        return aus

    def _schliessen(self, n, t, tot=False):
        a = self.offen.pop(n)
        echt = a["leben"] if tot else max(0.0, a["leben"] - a.get("leben_jetzt", a["leben"]))
        if a["nah"]:
            self.nahkampf += 1           # Nahkampf rechnet das Modell nicht - zaehlt nicht (Zahl steht im Bericht)
            return []
        if not a["da"] and not tot:
            self.nicht_da = getattr(self, "nicht_da", 0) + 1     # nie am Ziel: die Vorhersage galt fuer einen Weg, den er nicht ging
            return []
        alt = self.kalib
        self.vorher += a["vorher"]
        self.echt += echt
        self.zahl += 1
        self.partie[0] += 1
        self.partie[1] += a["vorher"]
        self.partie[2] += echt
        self.schreiben()
        return ["EICHUNG Angriff %d auf %s (%d Takte inkl. Nachlauf): vorhergesagt %d, echt %d%s -> KALIB %.3f -> %.3f "
                "(%d Angriffe, %d mit Nahkampf nicht gezaehlt)" % (n, a["ziel"], t - a["t"], a["vorher"], echt, " (tot)" if tot else "",
                                                                   alt, self.kalib, self.zahl, self.nahkampf)]

    def schreiben(self):
        if not self.datei:
            return
        try:
            os.makedirs(os.path.dirname(self.datei), exist_ok=True)
            tmp = self.datei + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"quelle": "risiko_lernen.Eichung (B-278/B-279)", "fassung": FASSUNG, "vorhergesagt": self.vorher, "echt": self.echt,
                           "angriffe": self.zahl, "kalib": self.kalib, "start": START, "prior": PRIOR}, f, indent=1)
            os.replace(tmp, self.datei)
        except OSError:
            pass
