# -*- coding: utf-8 -*-
"""Vorhersage-Tagebuch (B-273 Schritt 0, Plan_Gehirn_Meta.md; Daniel 27.10.2026 20:05 "ja fange an mit Schritt 0").

Jede Entscheidung schreibt VORHER auf, was sie erwartet, und das Ergebnis wird daneben gestellt - ohne dieses Tagebuch kann
der Selbstpruefer (Stufe 4) nichts lernen. Eine Zeile je Eintrag in daten/tagebuch_<stempel>_sp<n>.jsonl:
  {"t": Takt, "art": ..., "eingang": {...}, "vorhersage": Zahl, "gemessen": Zahl oder null, "verhaeltnis": gemessen/vorhersage}

Erste Kennzahl (art "lord_schaden"): Schaden je Takt am feindlichen Lord - vorhergesagt aus der Gefechtsrechnung
(gefecht.dps je eigener/verbuendeter Einheit bis LORD_NAH Felder, wie die MESSUNG-Zeile im Lenker), gemessen aus dem
Lebensverlust zwischen zwei Beobachtungen. Annahme (im Eintrag vermerkt): alle Einheiten in LORD_NAH Feldern schlagen den
Lord, weiter entfernte Schuetzen nicht.

Schalter: Tagebuch(an=False) schreibt nichts (Aufruf tagebuch=nein). Die eigene Rechenzeit wird mitgezaehlt (zeit_s)."""
import io
import json
import os
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
LORD = 55
LORD_NAH = 5            # wie die MESSUNG Feindlord im Lenker
MELDEN_JE = 10          # alle so viele Abgleiche eine Zusammenfassung
NACH_FRIST = 1500       # Lord-Angriff: Ergebnis spaetestens nach max(2 x vorhergesagte Takte, NACH_FRIST) Takten
AKTIV = None            # das Tagebuch des Lenkers (erstes_spiel.main) - Module rufen lord_angriff ohne es zu kennen


def lord_angriff(t, quelle, lord_nr, einheiten, zahlen):
    """B-273: ein Lord-Angriff beginnt - die Vorhersage des Lord-Wettlaufs (gefecht.LETZTES_RENNEN) merken; das Ergebnis
    schreibt lord_runde, sobald der Lord faellt oder die Frist um ist. Ohne Tagebuch oder ohne Zahlen: nichts."""
    if AKTIV is not None and AKTIV.an and zahlen:
        AKTIV.angriff_merken(t, quelle, lord_nr, einheiten, zahlen)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def lord_vorhersage(L, lord_nr, freunde):
    """(Schaden je Takt, {typ: anzahl}) der eigenen/verbuendeten Einheiten bis LORD_NAH Felder um den Lord lord_nr."""
    import gefecht
    tb = gefecht.tabelle()
    schaden, fern = tb[0], (tb[2] if len(tb) > 2 else None)
    lp = (L[lord_nr]["x"], L[lord_nr]["y"])
    summe, bei = 0.0, {}
    for u in L.values():
        if u["besitzer"] in freunde and u.get("leben", 1) > 0 and u["typ"] != LORD and schach((u["x"], u["y"]), lp) <= LORD_NAH:
            summe += gefecht.dps(u["typ"], LORD, schaden, fern, 1)
            bei[u["typ"]] = bei.get(u["typ"], 0) + 1
    return summe, bei


class Tagebuch(object):
    def __init__(self, sp, an=True, datei=None):
        self.sp, self.an = sp, an
        self.datei = datei or os.path.join(D, time.strftime("tagebuch_%Y%m%d_%H%M%S") + "_sp%d.jsonl" % sp)
        self.zeit_s, self.verhaeltnisse = 0.0, []
        self._lord = {}                       # lord_nr -> (takt, leben, vorhersage, eingang) der letzten Beobachtung
        self._angriffe = []                   # offene Lord-Angriffe mit ihrer Vorhersage
        self._L = {}

    def angriff_merken(self, t, quelle, lord_nr, einheiten, zahlen):
        if any(a["lord"] == lord_nr and a["quelle"] == quelle for a in self._angriffe):
            return
        leben = sum(self._L[n]["leben"] for n in einheiten if n in self._L)
        lord = self._L.get(lord_nr, {}).get("leben")
        self._angriffe.append({"t": t, "quelle": quelle, "lord": lord_nr, "einheiten": list(einheiten), "leben": leben,
                               "lord_leben": lord, "zahlen": zahlen})

    def _angriffe_pruefen(self, t, L):
        """Ergebnis jedes offenen Lord-Angriffs: Lord gefallen (nicht mehr im Lagebild) oder Frist um."""
        for a in list(self._angriffe):
            z = a["zahlen"]
            frist = max(2 * z.get("takte", 0), NACH_FRIST)
            gefallen = a["lord"] not in L or L[a["lord"]].get("leben", 0) <= 0
            if not gefallen and t - a["t"] < frist:
                continue
            self._angriffe.remove(a)
            rest = sum(L[n]["leben"] for n in a["einheiten"] if n in L)
            anteil = rest / float(a["leben"]) if a["leben"] else None
            lord_jetzt = 0 if gefallen else L[a["lord"]]["leben"]
            self.eintrag(t, "lord_wettlauf", z.get("takte") if z.get("faellt") else None,
                         (t - a["t"]) if gefallen else None,
                         {"quelle": a["quelle"], "lord": a["lord"], "vorhersage": z, "gefallen": gefallen,
                          "lord_leben": [a["lord_leben"], lord_jetzt], "einheiten": len(a["einheiten"]),
                          "rest_anteil_gemessen": round(anteil, 3) if anteil is not None else None,
                          "rest_anteil_vorhergesagt": z.get("rest_anteil"), "takte_seit_start": t - a["t"]})

    def eintrag(self, t, art, vorhersage, gemessen=None, eingang=None):
        if not self.an:
            return None
        t0 = time.perf_counter()
        z = {"t": t, "art": art, "eingang": eingang or {}, "vorhersage": round(vorhersage, 2) if vorhersage is not None else None,
             "gemessen": round(gemessen, 2) if gemessen is not None else None,
             "verhaeltnis": round(gemessen / vorhersage, 3) if gemessen is not None and vorhersage else None}
        with io.open(self.datei, "a", encoding="utf-8") as f:
            f.write(json.dumps(z, ensure_ascii=False) + "\n")
        if z["verhaeltnis"] is not None:
            self.verhaeltnisse.append(z["verhaeltnis"])
        self.zeit_s += time.perf_counter() - t0
        return z

    def lord_runde(self, t, L, freunde, feind_von):
        """Jede Runde: fuer jeden feindlichen Lord die Vorhersage dieser Runde merken; hat er seit der letzten Runde Leben
        verloren, den gemessenen Schaden je Takt neben die damalige Vorhersage schreiben. Gibt Meldungen zurueck."""
        if not self.an:
            return []
        t0 = time.perf_counter()
        aus = []
        self._L = L
        self._angriffe_pruefen(t, L)
        for n, e in L.items():
            if e["typ"] != LORD or not feind_von(e["besitzer"]):
                continue
            alt = self._lord.get(n)
            v, bei = lord_vorhersage(L, n, freunde)
            # 27.10. (Rueckwaerts-Messung 180423/192840: von 5-8 Einheiten am Lord schlugen meist 0-2 sichtbar zu): mitschreiben,
            # wie viele eigene Einheiten in diesem Moment sichtbar auf den Lord schlagen/schiessen (eigene Felder - fair)
            schlagen = sum(1 for u in L.values() if u["besitzer"] in freunde and (
                (u.get("zustand") == 106 and u.get("nahziel") == n) or (u.get("zielart") == 4 and u.get("zieleinheit") == n)))
            if alt is not None and e["leben"] < alt[1] and t > alt[0] and alt[2] > 0:
                gemessen = (alt[1] - e["leben"]) / float(t - alt[0])
                z = self.eintrag(t, "lord_schaden", alt[2], gemessen,
                                 {"lord": n, "von_takt": alt[0], "leben": [alt[1], e["leben"]], "bei": alt[3],
                                  "schlagen_sichtbar": alt[4], "annahme": "alle bis %d Felder schlagen den Lord" % LORD_NAH})
                if z and len(self.verhaeltnisse) % MELDEN_JE == 0:
                    aus.append(self.zusammenfassung())
            self._lord[n] = (t, e["leben"], v, bei, schlagen)
        self.zeit_s += time.perf_counter() - t0
        return aus

    def zusammenfassung(self):
        v = sorted(self.verhaeltnisse)
        med = v[len(v) // 2] if v else None
        return "TAGEBUCH: %d Abgleiche Lord-Schaden, gemessen/vorhergesagt Median %s (Mitte 50 %%: %s - %s), Rechenzeit %.3f s" % (
            len(v), med, v[len(v) // 4] if v else None, v[(3 * len(v)) // 4] if v else None, self.zeit_s)
