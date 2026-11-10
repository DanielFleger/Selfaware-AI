# -*- coding: utf-8 -*-
"""B-182 Fehlerwache (Daniel 10.11. 23:16: "Erst Partie mit Wache / nutze mal die ersten 20 einheiten die bei uns auf dem feld
sind als basis zum schauen / unsere ki soll maximal 20 einheiten haben insgesamt ich will sehen ob sie sich dran haelt / dann
spiel starten"; 22:51: "neue spiele auswerten aber eben nur soweit bis ein fehler auftritt ... dann lieber neu starten").

Eigener Prozess neben dem Lenker. Liest den Kern selbst (kern_leitung.Leitung), unabhaengig von dem, was der Lenker glaubt,
und haelt beim ERSTEN Fehler an: Spiel pausieren, Lenker ueber die STOP-Datei beenden, Bericht schreiben.

Beobachtet werden die ersten BEOBACHTEN eigenen Kaempfer (ohne Lord), in der Reihenfolge, in der sie auftauchen. Die
Obergrenze zaehlt alle eigenen Kaempfer.
  F1 Obergrenze   mehr als GRENZE eigene Kaempfer leben
  F2 steht        eine beobachtete Einheit hat ein Angriffsziel (Schussziel, Angriffsziel oder Gebaeude), bewegt sich nicht,
                  hat kein Laufziel und kaempft nicht (Ziel ausser Reichweite) - STILL Takte lang
  F3 untaetig     ein beobachteter Soeldner (Typ 70 bis 76) steht zu Hause ohne Angriffsziel und kaempft nicht - UNTAETIG Takte
  F4 ohne Taeter  ein Modul meldet einen getoeteten Arbeiter ("REITERJAGD: Reiter R hat Arbeiter A erledigt",
                  "NAHKAMPF-RAID: R (Typ T) hat Arbeiter A erledigt"), aber R hatte A in den letzten BELEG Takten weder als
                  Schuss- noch als Nahkampfziel
STILL, UNTAETIG und BELEG sind selbst gesetzt, nicht gemessen. Reichweiten aus services/spielwerte.py.

Aufruf: python -m selfaware.tools.checks.fehlerwache --instanz 2 [--grenze 20] [--beobachten 20] [--still 600]
        [--untaetig 2000] [--beleg 600] [--minuten 30]
Rueckgabe: 0 = Partie ohne Fehler zu Ende, 2 = Fehler gefunden und angehalten, 1 = keine Partie gesehen.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

import selfaware.services.spielwerte as SW
from selfaware.baukasten.obergrenze import LORD, kaempfer

SOELDNER = frozenset(range(70, 77))
HEIM_FELDER = 40        # selbst gesetzt: so nah am eigenen Lord gilt eine Einheit als zu Hause
NAH_FELDER = 3          # Nahkampf: Ziel hoechstens so weit (Schach)
GEBAEUDE_FELDER = 4     # Gebaeudeangriff: am Gebaeude, wenn hoechstens so weit vom Gebaeudeort (Schach)
ANSPRUCH = re.compile(r"(REITERJAGD: Reiter|NAHKAMPF-RAID:) (\d+) (?:\(Typ \d+\) )?hat Arbeiter (\d+) erledigt")


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ort(e):
    return (e["x"], e["y"])


class Wache:
    def __init__(self, sp=1, grenze=20, beobachten=20, still=600, untaetig=2000, beleg=600):
        self.sp, self.grenze, self.beobachten = sp, grenze, beobachten
        self.still, self.untaetig, self.beleg = still, untaetig, beleg
        self.gruppe = []          # Nummern der beobachteten Einheiten, in der Reihenfolge des Auftauchens
        self.art = {}             # Nummer -> Art beim ersten Sehen (eine Nummer kann spaeter eine andere Einheit tragen)
        self.letzt = {}           # Nummer -> (Ort, Takt der letzten Bewegung oder des letzten Kampfes)
        self.leer_seit = {}       # Nummer -> Takt, seit dem der Soeldner untaetig zu Hause steht
        self.ziele = {}           # (eigene Nummer, Opfer) -> letzter Takt mit diesem Schuss- oder Nahkampfziel
        self.heim = None
        self.hoechst = 0
        self.zustaende = {}       # Nummer -> {zustand: Takte} fuer den Bericht

    def _zustand(self, e, welt):
        """(Angriffsziel vorhanden, kaempft, Beschreibung des Ziels)."""
        p = ort(e)
        r = SW.erfassen(e["typ"])
        feind = lambda n: welt.einheiten.get(n) if n and welt.einheiten.get(n, {}).get("besitzer") not in (None, 0, self.sp) else None  # noqa: E731
        nah = feind(e.get("nahziel"))
        if nah is not None and schach(p, ort(nah)) <= NAH_FELDER:
            return True, True, "Nahkampf mit %d" % e["nahziel"]
        schuss = feind(e.get("schusseinheit")) or (feind(e.get("zieleinheit")) if e.get("zielart") == 4 else None)
        if schuss is not None:
            n = e.get("schusseinheit") or e.get("zieleinheit")
            d = schach(p, ort(schuss))
            if r is not None and SW.luftlinie2(p, ort(schuss)) <= r * r:
                return True, True, "schiesst auf %d in %d Feldern" % (n, d)
            if r is None and d <= NAH_FELDER:
                return True, True, "am Ziel %d" % n
            return True, False, "Ziel %d in %d Feldern" % (n, d)
        mauer = (e.get("mauerx", 0), e.get("mauery", 0))
        if mauer != (0, 0):
            d = schach(p, mauer)
            return True, d <= GEBAEUDE_FELDER, "Gebaeude bei %s in %d Feldern" % (mauer, d)
        return False, False, "ohne Angriffsziel"

    def schritt(self, welt, anspruechen=()):
        """Ein Stand des Kerns (welt) und neue Erfolgsmeldungen [(Modul, eigene Nummer, Opfer)] -> Liste der Fehler (leer = gut)."""
        t = welt.tick
        fehler = []
        lords = [e for e in welt.einheiten.values() if e.get("besitzer") == self.sp and e.get("typ") == LORD]
        if self.heim is None and lords:
            self.heim = ort(lords[0])
        alle = kaempfer(welt, self.sp)
        self.hoechst = max(self.hoechst, len(alle))
        if len(alle) > self.grenze:
            fehler.append({"art": "F1 Obergrenze", "takt": t, "text": "%d eigene Kaempfer bei Grenze %d" % (len(alle), self.grenze),
                           "einheiten": alle})
        for n in alle:
            e = welt.einheiten[n]
            if n not in self.art and len(self.gruppe) < self.beobachten:
                self.gruppe.append(n)
                self.art[n] = e["typ"]
            for opfer in (e.get("schusseinheit"), e.get("nahziel")):     # Belege fuer F4 von allen eigenen Kaempfern
                if opfer:
                    self.ziele[(n, opfer)] = t
        for n in self.gruppe:
            e = welt.einheiten.get(n)
            if e is None or e.get("besitzer") != self.sp or e.get("typ") != self.art[n] or e.get("leben", 1) <= 0:
                self.letzt.pop(n, None)
                self.leer_seit.pop(n, None)
                continue
            p = ort(e)
            hat_ziel, kaempft, was = self._zustand(e, welt)
            lauf = (e.get("laufx", 0), e.get("laufy", 0))
            unterwegs = lauf not in ((0, 0), p)
            alt = self.letzt.get(n)
            if alt is None or alt[0] != p or kaempft or unterwegs:
                self.letzt[n] = (p, t)
            elif hat_ziel and t - alt[1] >= self.still:
                fehler.append({"art": "F2 steht", "takt": t, "einheit": n, "typ": e["typ"], "ort": p,
                               "text": "%s seit %d Takten ohne Weg und ohne Kampf" % (was, t - alt[1])})
            zustand = "kaempft" if kaempft else ("laeuft" if (alt is None or alt[0] != p or unterwegs) else
                                                 ("steht_mit_ziel" if hat_ziel else "steht_ohne_ziel"))
            z = self.zustaende.setdefault(n, {})
            z[zustand] = z.get(zustand, 0) + 1
            zuhause = self.heim is not None and schach(p, self.heim) <= HEIM_FELDER
            if e["typ"] in SOELDNER and zuhause and not hat_ziel and not kaempft and not unterwegs and (alt is None or alt[0] == p):
                seit = self.leer_seit.setdefault(n, t)
                if t - seit >= self.untaetig:
                    fehler.append({"art": "F3 untaetig", "takt": t, "einheit": n, "typ": e["typ"], "ort": p,
                                   "text": "Soeldner seit %d Takten zu Hause ohne Angriffsziel" % (t - seit)})
            else:
                self.leer_seit.pop(n, None)
        for modul, wer, opfer in anspruechen:
            zuletzt = self.ziele.get((wer, opfer))
            if zuletzt is None or t - zuletzt > self.beleg:
                fehler.append({"art": "F4 ohne Taeter", "takt": t, "einheit": wer, "opfer": opfer,
                               "text": "%s meldet Arbeiter %d erledigt, Einheit %d hatte ihn %s nicht als Ziel" % (
                                   modul, opfer, wer, "nie" if zuletzt is None else "seit %d Takten" % (t - zuletzt))})
        return fehler

    def bericht(self):
        return {"gruppe": [(n, self.art[n]) for n in self.gruppe], "hoechst": self.hoechst, "zustaende": self.zustaende}


def anspruechen_aus(text):
    """[(Modul, eigene Nummer, Opfer)] aus neuen Zeilen der Mitschrift."""
    return [("Reiterjagd" if m.group(1).startswith("REITER") else "Nahkampf-Raid", int(m.group(2)), int(m.group(3)))
            for m in ANSPRUCH.finditer(text)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--instanz", type=int, required=True)
    p.add_argument("--grenze", type=int, default=20)
    p.add_argument("--beobachten", type=int, default=20)
    p.add_argument("--still", type=int, default=600)
    p.add_argument("--untaetig", type=int, default=2000)
    p.add_argument("--beleg", type=int, default=600)
    p.add_argument("--minuten", type=float, default=30)
    a = p.parse_args()
    if a.instanz in (4, 5):
        sys.exit("Instanz 4 gehoert SAI, Instanz 5 ist Daniels Spiel")
    os.environ["SHC_INSTANZ"] = str(a.instanz)
    from selfaware import workspace
    from selfaware.game.kern_leitung import Leitung
    from selfaware.game.ucp.befehl import SPIEL
    from selfaware.game.ucp.laden import befehl
    le = Leitung(SPIEL)
    forschung = os.path.join(workspace.DATA, "research")
    start = time.time()
    t0 = le.lesen().tick
    print("FEHLERWACHE: warte auf eine neue Partie (Kern steht bei Takt %d)" % t0, flush=True)
    zurueck = t0 == 0
    while True:            # neue Partie: der Takt springt unter den Anfangswert zurueck und laeuft dann wieder
        w = le.lesen()
        zurueck = zurueck or w.tick < t0
        if zurueck and w.tick > 0:
            break
        if time.time() - start > 300:
            print("FEHLERWACHE: nach 5 Minuten keine neue Partie", flush=True)
            return 1
        time.sleep(0.3)
    wache = Wache(1, a.grenze, a.beobachten, a.still, a.untaetig, a.beleg)
    konsole, gelesen = None, 0
    naechster_bericht, letzter_tick, gleich_seit = 2000, -1, time.time()
    print("FEHLERWACHE: Partie laeuft (Takt %d) - Grenze %d, beobachtet die ersten %d Kaempfer, still %d, untaetig %d, Beleg %d"
          % (w.tick, a.grenze, a.beobachten, a.still, a.untaetig, a.beleg), flush=True)
    while time.time() - start < a.minuten * 60:
        w = le.lesen()
        if w.tick == letzter_tick:
            if time.time() - gleich_seit > 60:
                print("FEHLERWACHE: Takt steht seit 60 s bei %d - Partie vorbei, kein Fehler" % w.tick, flush=True)
                return 0
            time.sleep(0.2)
            continue
        letzter_tick, gleich_seit = w.tick, time.time()
        if konsole is None:
            neu = [k for k in glob.glob(os.path.join(forschung, "aufstellung_*_konsole.txt")) if os.path.getmtime(k) >= start]
            konsole = max(neu, key=os.path.getmtime) if neu else None
        text = ""
        if konsole:
            with open(konsole, "rb") as f:
                f.seek(gelesen)
                roh = f.read()
            gelesen += len(roh)
            text = roh.decode("utf-8", "replace")
        fehler = wache.schritt(w, anspruechen_aus(text))
        if w.tick >= naechster_bericht:
            naechster_bericht = w.tick + 2000
            z = {}
            for d in wache.zustaende.values():
                for k, v in d.items():
                    z[k] = z.get(k, 0) + v
            print("FEHLERWACHE Takt %d: %d Kaempfer (hoechstens %d), beobachtet %d, Zustaende %s" % (
                w.tick, len(kaempfer(w, 1)), wache.hoechst, len(wache.gruppe), z), flush=True)
        if fehler:
            open(os.path.join(workspace.STATE, "STOP"), "w").close()
            befehl({"pause": True}, 0.5)
            stempel = time.strftime("%Y%m%d_%H%M%S")
            pfad = os.path.join(forschung, "fehlerwache_%s_i%d.json" % (stempel, a.instanz))
            json.dump({"fehler": fehler, "takt": w.tick, "konsole": konsole and os.path.basename(konsole), **wache.bericht()},
                      open(pfad, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
            for f_ in fehler:
                print("FEHLERWACHE FEHLER %s bei Takt %d: %s" % (f_["art"], f_["takt"], f_["text"]), flush=True)
            print("FEHLERWACHE: Spiel angehalten, Lenker ueber STOP beendet, Bericht %s" % pfad, flush=True)
            return 2
        time.sleep(0.2)
    print("FEHLERWACHE: Zeitgrenze erreicht, kein Fehler", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
