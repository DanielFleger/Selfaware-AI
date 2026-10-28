# -*- coding: utf-8 -*-
"""Schadens-Tagebuch und Eichkurve (B-286; Daniel 28.10. 01:15 "der erwartete Schaden ist nicht richtig geeicht", 01:21 "ok";
Plan_Schaden_Gemessen.md nach Frage-Agent rot 01:20: die Lerner-Raten messen etwas anderes - jeder Schuetze in Reichweite, auch
hinter Gebaeuden, auch unsichtbar, auch Nahkampf).

Je Runde und eigener Assassine: was das Modell an ihrem Ort vorhersagte (sicht.Lage.beschuss(ort, nr=n) - Sicht, freie
Linie, Zuteilung der Schuetzen) x Takte bis zur naechsten Runde, gegen ihren echten Lebensverlust in dieser Zeit. Nicht
gezaehlt: Runden, in denen sie im Nahkampf stand (das Modell rechnet nur Beschuss). Gesammelt je STUFE der Vorhersage
(Schaden je Takt): so entsteht eine Eichkurve statt eines Faktors - echt/vorhergesagt je Stufe.
faktor(dps): Kurve der Stufe, sobald dort MIN_TAKTE gesammelt sind; sonst None (der Aufrufer nimmt seinen bisherigen Wert -
in der Meldung als Ersatz sichtbar). Gespeichert je Lernprofil (SHC_LEARNING_DIR), ohne Profil nur im Speicher.
Rueckweg: assassinen.SCHADEN_KURVE = False."""
import json
import os

STUFEN = (0.5, 5.0, 25.0, 100.0, 400.0)      # Grenzen der Vorhersage je Takt; Stufe i = bis STUFEN[i], letzte = darueber
MIN_TAKTE = 3000                             # so viele Takte je Stufe, bevor ihr Faktor gilt (Startwert, UNGEMESSEN)
GRENZEN = (0.01, 3.0)
FASSUNG = 1


def stufe(dps):
    for i, g in enumerate(STUFEN):
        if dps <= g:
            return i
    return len(STUFEN)


def pfad(typ):
    """Je Einheitentyp eine Kurve (Assassine 73 zuerst; Reiter, Sklaven, Heer sollen denselben Baustein nutzen)."""
    d = os.environ.get("SHC_LEARNING_DIR")
    return os.path.join(d, "schadens_kurve_%d.json" % typ) if d else None


class Kurve:
    def __init__(self, typ, datei=None):
        self.typ = typ
        self.datei = datei or pfad(typ)
        self.st = [{"vorher": 0.0, "echt": 0.0, "takte": 0} for _ in range(len(STUFEN) + 1)]
        try:
            d = json.load(open(self.datei, encoding="utf-8")) if self.datei else {}
            if d.get("fassung") == FASSUNG and len(d.get("stufen", [])) == len(self.st):
                self.st = [dict(vorher=float(s["vorher"]), echt=float(s["echt"]), takte=int(s["takte"])) for s in d["stufen"]]
        except (OSError, ValueError, KeyError, TypeError):
            pass
        self.letzt = {}          # Einheit -> (Takt, Leben, Vorhersage je Takt, im Nahkampf)
        self.runden = 0

    def faktor(self, dps):
        s = self.st[stufe(dps)]
        if s["takte"] < MIN_TAKTE or s["vorher"] <= 0:
            return None
        return min(GRENZEN[1], max(GRENZEN[0], s["echt"] / s["vorher"]))

    def runde(self, t, einheiten, vorhersage):
        """einheiten: {n: {"leben", "nahangreifer"}} der eigenen Assassinen; vorhersage(n) -> Schaden je Takt am Ort jetzt."""
        for n, e in einheiten.items():
            alt = self.letzt.get(n)
            nah = (e.get("nahangreifer") or 0) > 0
            if alt is not None and t > alt[0] and not nah and not alt[3]:
                dt = t - alt[0]
                s = self.st[stufe(alt[2])]
                s["vorher"] += alt[2] * dt
                s["echt"] += max(0.0, alt[1] - float(e.get("leben", alt[1])))
                s["takte"] += dt
            try:
                v = float(vorhersage(n))
            except Exception:
                v = 0.0
            self.letzt[n] = (t, float(e.get("leben", 0)), v, nah)
        for n in [n for n in self.letzt if n not in einheiten]:
            del self.letzt[n]                       # tot oder weg: der Rest des Lebens ist nicht sicher Beschuss - nicht gezaehlt
        self.runden += 1
        if self.runden % 20 == 0:
            self.schreiben()

    def bericht(self):
        return "; ".join("Stufe bis %s: %d Takte, vorhergesagt %d, echt %d%s" % (
            STUFEN[i] if i < len(STUFEN) else "mehr", s["takte"], s["vorher"], s["echt"],
            " -> Faktor %.3f" % (s["echt"] / s["vorher"]) if s["vorher"] > 0 and s["takte"] >= MIN_TAKTE else "")
            for i, s in enumerate(self.st) if s["takte"])

    def schreiben(self):
        if not self.datei:
            return
        try:
            os.makedirs(os.path.dirname(self.datei), exist_ok=True)
            tmp = self.datei + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"quelle": "schadens_tagebuch (B-286)", "fassung": FASSUNG, "stufen_grenzen": STUFEN, "stufen": self.st}, f,
                          indent=1)
            os.replace(tmp, self.datei)
        except OSError:
            pass
